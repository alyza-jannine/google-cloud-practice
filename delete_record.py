import logging
import os

from flask import Flask, request, jsonify
import sqlalchemy

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

app = Flask(__name__)

logger = logging.getLogger()

db = sqlalchemy.create_engine(
    sqlalchemy.engine.url.URL(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_pass,
        database=db_name,
        query={"unix_socket": "/cloudsql/{}".format(cloud_sql_connection_name)},
    ),
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800
)

@app.route("/", methods=["DELETE"])
def delete_record(request):    
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    id_array = request.form['id_array']
    array_str = id_array.strip("[]")
    
    stmt = sqlalchemy.text(
        f"DELETE FROM recordsinserted WHERE record_id in ({array_str})"
    )

    try:
        with db.connect() as conn:
            conn.execute(stmt)
    except Exception as e:
        return ('Unable to delete record(s).', 500, headers)
        
    resp = 'Successfully delete record(s).'

    return (resp, 200, headers)
