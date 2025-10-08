import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from flask import current_app

# Initialize connection pool globally
def init_db_pool():
    db_config = {
        "host": current_app.config.get('RDS_MYSQL_HOST'),
        "port": int(current_app.config.get('RDS_MYSQL_PORT')) if current_app.config.get('RDS_MYSQL_PORT') else 3306,
        "user": current_app.config.get('RDS_MYSQL_USER'),
        "password": current_app.config.get('RDS_MYSQL_PASS'),
        "database": current_app.config.get('RDS_MYSQL_DB')
    }

    pool_config = {
        "pool_name": "mysql_pool",
        "pool_size": 5,
        "pool_reset_session": True,
        **db_config
    }

    try:
        connection_pool = MySQLConnectionPool(**pool_config)
        print("Connection pool created successfully")
        return connection_pool
    except mysql.connector.Error as err:
        print(f"Error creating connection pool: {err}")
        raise

# Global connection pool
connection_pool = None

def get_data_from_rds(kwargs, page=1, page_size=10, sort_by='year', sort_direction='ASC'):
    # Initialize connection pool if not already done
    global connection_pool
    if connection_pool is None:
        connection_pool = init_db_pool()

    # Validate pagination parameters
    page = max(1, page)
    page_size = min(page_size, 100)  # MAX_PAGE_SIZE
    offset = (page - 1) * page_size

    # Validate sorting parameters
    allowed_sort_columns = {'year', 'anzsic', 'data_value'}
    sort_by = sort_by if sort_by in allowed_sort_columns else 'year'
    sort_direction = sort_direction.upper() if sort_direction.upper() in ('ASC', 'DESC') else 'ASC'

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