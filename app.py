from flask import Flask, render_template, request, jsonify
import psycopg2
import os

# Get the database URL from the environment variable or use a default value
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://shiru:default@db:5432/shiru')

db_params = {
    'host': 'db',
    'port': '5432',
    'database': 'Database Name',
    'user': 'User',
    'password': 'default'
    }

app = Flask(__name__)

def execute_query(query):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return columns, rows
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query = data.get('query', '')
    columns, rows = execute_query(query)
    if columns:
        return jsonify({'success': True, 'columns': columns, 'rows': rows})
    else:
        return jsonify({'success': False, 'error': 'Invalid query'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
