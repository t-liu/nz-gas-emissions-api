import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from flask import Flask, request, jsonify
import redis
import json
import hashlib

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# Initialize connection pool globally
db_config = {
    "host": app.config.get('RDS_MYSQL_HOST'),
    "port": int(app.config.get('RDS_MYSQL_PORT')) if app.config.get('RDS_MYSQL_PORT') else 3306,
    "user": app.config.get('RDS_MYSQL_USER'),
    "password": app.config.get('RDS_MYSQL_PASS'),
    "database": app.config.get('RDS_MYSQL_DB')
}

# Configure the connection pool
pool_config = {
    "pool_name": "mysql_pool",
    "pool_size": 5,
    "pool_reset_session": True,
    **db_config
}

# Create the connection pool
try:
    connection_pool = MySQLConnectionPool(**pool_config)
    print("Connection pool created successfully")
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    raise

# Initialize Redis connection
redis_config = {
    "host": app.config.get('REDIS_HOST', 'localhost'),
    "port": app.config.get('REDIS_PORT', 6379),
    "db": app.config.get('REDIS_DB', 0),
    "password": app.config.get('REDIS_PASSWORD', None)
}

try:
    redis_client = redis.Redis(**redis_config)
    redis_client.ping()
    print("Redis connection established successfully")
except redis.RedisError as err:
    print(f"Error connecting to Redis: {err}")
    redis_client = None  # Fallback to no caching if Redis fails

# Pagination settings
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 10

# Allowed columns for sorting
ALLOWED_SORT_COLUMNS = {'year', 'anzsic', 'data_value'}
DEFAULT_SORT_COLUMN = 'year'
DEFAULT_SORT_DIRECTION = 'ASC'

# Cache settings
CACHE_TTL = 300  # Cache expiry in seconds (5 minutes)

def serialize_emission(result):
    """Map database result to response format."""
    return {
        'year': result['year'],
        'anzsic': result['anzsic'],
        'anzwi': result['anzwi'],
        'description': result['anzsic_descriptor'],
        'category': result['category'],
        'variable': result['variable'],
        'units': result['units'],
        'magnitude': result['magnitude'],
        'source': result['source'],
        'data_value': result['data_value']
    }

def generate_cache_key(endpoint, params):
    """Generate a unique cache key based on endpoint and query parameters."""
    # Sort params to ensure consistent keys
    sorted_params = sorted(params.items())
    # Create a string representation of the params
    param_str = json.dumps(sorted_params, sort_keys=True)
    # Use a hash to keep the key length manageable
    return f"{endpoint}:{hashlib.md5(param_str.encode('utf-8')).hexdigest()}"

def get_data_from_rds(kwargs, page=1, page_size=DEFAULT_PAGE_SIZE, sort_by=DEFAULT_SORT_COLUMN, sort_direction=DEFAULT_SORT_DIRECTION):
    # Validate pagination parameters
    page = max(1, page)
    page_size = min(page_size, MAX_PAGE_SIZE)
    offset = (page - 1) * page_size

    # Validate sorting parameters
    sort_by = sort_by if sort_by in ALLOWED_SORT_COLUMNS else DEFAULT_SORT_COLUMN
    sort_direction = sort_direction.upper() if sort_direction.upper() in ('ASC', 'DESC') else DEFAULT_SORT_DIRECTION

    # Get a connection from the pool
    try:
        conn = connection_pool.get_connection()
    except mysql.connector.Error as err:
        return {
            'data': [],
            'error': f"Failed to get database connection: {str(err)}",
            'total_count': 0
        }

    # Define specific columns to select
    columns = [
        'year',
        'anzsic',
        'anzwi',
        'anzsic_descriptor',
        'category',
        'variable',
        'units',
        'magnitude',
        'source',
        'data_value'
    ]

    try:
        with conn.cursor(dictionary=True) as cur:
            # Build base query
            base_query = f"SELECT {', '.join(['`' + col + '`' for col in columns])} FROM emissions"
            count_query = "SELECT COUNT(*) as total_count FROM emissions"
            values = []

            # Add WHERE clause if filters are provided
            if kwargs:
                where = 'WHERE ' + ' AND '.join(['`' + k + '` = %s' for k in kwargs.keys()])
                base_query += f" {where}"
                count_query += f" {where}"
                values.extend(list(kwargs.values()))

            # Add sorting
            base_query += f" ORDER BY `{sort_by}` {sort_direction}"

            # Add pagination
            base_query += " LIMIT %s OFFSET %s"
            values.extend([page_size, offset])

            # Execute count query
            cur.execute(count_query, values[:len(kwargs)] if kwargs else [])
            total_count = cur.fetchone()['total_count']

            # Execute data query
            cur.execute(base_query, values)
            details = cur.fetchall()

            # Return empty list for empty result sets
            if not details:
                return {
                    'data': [],
                    'error': None,
                    'total_count': total_count
                }

            return {
                'data': details,
                'error': None,
                'total_count': total_count
            }

    except mysql.connector.Error as err:
        error_message = (
            "Authentication error: Invalid username or password" if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR else
            "Database error: Database does not exist" if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR else
            f"Database error: {str(err)}"
        )
        return {
            'data': [],
            'error': error_message,
            'total_count': 0
        }
    finally:
        if conn.is_connected():
            conn.close()
            print("Connection returned to pool")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/emissions', methods=['GET'])
def get_data_pagination():
    # Query parameters for pagination and sorting
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', DEFAULT_PAGE_SIZE, type=int)
    sort_by = request.args.get('sort_by', DEFAULT_SORT_COLUMN)
    sort_direction = request.args.get('sort_direction', DEFAULT_SORT_DIRECTION)

    # Query parameters for filtering
    if request.args:
        kwargs = {k: v for k, v in request.args.items() if k not in ('page', 'page_size', 'sort_by', 'sort_direction')}
    else:
        print('No query string received')
        kwargs = None

    # Generate cache key
    cache_key = generate_cache_key('emissions', request.args)
    
    # Try to get data from cache
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                print("Cache hit")
                return jsonify(json.loads(cached_data)), 200
        except redis.RedisError as err:
            print(f"Redis error: {err}")
            # Continue without cache on Redis failure

    # Call RDS for data with pagination and sorting
    result = get_data_from_rds(kwargs, page, page_size, sort_by, sort_direction)
    
    # Handle error case
    if result['error']:
        response = {
            'data': [],
            'error': result['error'],
            'pagination': {
                'page': page,
                'page_size': min(page_size, MAX_PAGE_SIZE),
                'max_page_size': MAX_PAGE_SIZE,
                'total_count': result['total_count'],
                'total_pages': (result['total_count'] + min(page_size, MAX_PAGE_SIZE) - 1) // min(page_size, MAX_PAGE_SIZE)
            }
        }
        # Cache error responses for a shorter TTL (e.g., 30 seconds) to avoid repeated failed queries
        if redis_client:
            try:
                redis_client.setex(cache_key, 30, json.dumps(response))
            except redis.RedisError as err:
                print(f"Redis error while caching: {err}")
        return jsonify(response), 500 if 'error' in result['error'].lower() else 400

    # Map results to response format
    final_data = [serialize_emission(result) for result in result['data']]

    # Build response with pagination metadata
    response = {
        'data': final_data,
        'pagination': {
            'page': page,
            'page_size': min(page_size, MAX_PAGE_SIZE),
            'max_page_size': MAX_PAGE_SIZE,
            'total_count': result['total_count'],
            'total_pages': (result['total_count'] + min(page_size, MAX_PAGE_SIZE) - 1) // min(page_size, MAX_PAGE_SIZE)
        }
    }

    # Cache the response
    if redis_client:
        try:
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(response))
            print("Cache set")
        except redis.RedisError as err:
            print(f"Redis error while caching: {err}")

    return jsonify(response), 200

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0')