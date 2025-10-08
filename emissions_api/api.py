from flask import request, jsonify
from emissions_api.db import get_data_from_rds
from emissions_api.cache import get_cached_response, cache_response
from emissions_api.serializers import serialize_emission

# Pagination settings
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 10

# Sorting settings
ALLOWED_SORT_COLUMNS = {'year', 'anzsic', 'data_value'}
DEFAULT_SORT_COLUMN = 'year'
DEFAULT_SORT_DIRECTION = 'ASC'

def init_routes(app):
    """Register routes with the Flask app."""
    @app.route('/health', methods=['GET'])
    def index():
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

        # Check cache
        cached_response = get_cached_response('emissions', request.args)
        if cached_response:
            print("Cache hit")
            return jsonify(cached_response), 200

        # Call RDS for data
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
            # Cache error responses for a shorter TTL
            cache_response('emissions', request.args, response, ttl=30)
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
        cache_response('emissions', request.args, response)
        print("Cache set")

        return jsonify(response), 200

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'error': 'Resource not found'}), 404