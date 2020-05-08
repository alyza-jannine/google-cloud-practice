import logging
import os

from flask import Flask, request, jsonify, render_template
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


@app.route("/", methods=["GET"])
def retrieve_record(request):    
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    records = []
    with db.connect() as conn:
        # Execute the query and fetch all results
        all_records = conn.execute(
            "SELECT record_id, name, position, office, age, start_date, salary FROM recordsinserted "
            "ORDER BY start_date DESC"
        ).fetchall()
        # Convert the results into a list of dicts representing votes
        for row in all_records:
            records.append({"Id": row[0], "Name": row[1], "Position": row[2], "Office": row[3], "Age": row[4], "Start_Date": row[5], "Salary": row[6]})

    return (jsonify(records), 200, headers)
