import mysql.connector
import aws_credentials
import configparser

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session 

# default paginiation values
pageNumber = 0
pageSize = 5

app = Flask(__name__)
app.config["DEBUG"] = True


def get_data_from_rds(kwargs):

    config = configparser.ConfigParser()
    config.read('config.ini')

    conn = mysql.connector.connect(
        host = config['mysql']['host'],
        port = config['mysql']['port'],
        user = config['mysql']['user'],
        password = config['mysql']['pass'],
        db = config['mysql']['database']
        )

    try:
        with conn.cursor(dictionary = True) as cur:

            if kwargs:
                where = 'WHERE ' + ' AND ' .join(['`' + k + '` = %s' for k in kwargs.keys()])
                values = list(kwargs.values())
                query = 'SELECT * FROM emissions ' + where
                cur.execute(query, values)
            else:
                query = 'SELECT * FROM emissions LIMIT 5'
                cur.execute(query)
            details = cur.fetchall()
            return details
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        if conn.is_connected():
            conn.close()
            print("db connection is closed")


@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'ok'}), 200

@app.route('/emissions', methods=['GET'])
def get_data_pagination():
    # set the pagination configuration
    # page = request.args.get('page', 1, type=int)
    
    # query parameters
    if request.args:
        kwargs = (dict(request.args.items())) # store a dictionary of the query string
        # serialized = ", ".join(f"{k}: {v}" for k, v in request.args.items())  -- create a string to display the parameters & values
    else:
        print('No query string received')
        kwargs = None

    # call rds for data
    raw_data = get_data_from_rds(kwargs)
    
    # map
    final_data = []
    content = {}

    for result in raw_data:
        content = {
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
        final_data.append(content)
        content = {}

    return jsonify(final_data)

@app.errorhandler(404)
def page_not_found(e):
    #return "<h1>404</h1><p>The resource could not be found.</p>", 404
    return jsonify({'error': 'resource could not found'}), 404

if __name__ == "__main__":   
    app.run(debug = True, host='0.0.0.0')