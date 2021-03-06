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


@app.route("/", methods=["POST"])
def edit_record(request):    
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    record_id = request.form['Id']
    name = request.form['Name']
    position = request.form['Position']
    office = request.form['Office']
    age = request.form['Age']
    start_date = request.form['Start_Date']
    salary = request.form['Salary']
    

    stmt = sqlalchemy.text(
        "UPDATE recordsinserted SET"
        " name=:name,"
        " position=:position,"
        " office=:office,"
        " age=:age,"
        " start_date=:start_date,"
        " salary=:salary"
        " WHERE record_id=:record_id"
    )

    try:
        with db.connect() as conn:
            conn.execute(stmt, name=name, position=position, office=office, age=age, start_date=start_date, salary=salary, record_id=record_id)
    except Exception as e:
        return ('Unable to update record.', 500, headers)

    resp = f'Successfully updated record with Name: {name}, Position: {position}, Office: {office}, Age: {age}, Start Date: {start_date}, and Salary: {salary}'

    return (jsonify(resp), 200, headers)
