from flask import Flask
import mysql.connector
import json
from flask import jsonify, request
from datetime import datetime as dt

app = Flask(__name__)
app.secret_key = "tidb"
app.config['MYSQL_HOST'] = '192.168.16.21'
app.config['MYSQL_PORT'] = 4000
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ufo'

db = mysql.connector.connect(
	host="192.168.16.21",
	user="root",
	passwd="",
	database="ufo",
	port=4000
)

@app.route('/ufo', methods = ['GET'])
def get_ufo():
    csr = db.cursor()
    csr.execute("select * from ufo_data")
    data=[]
    for (id, datetime, city, state, country, shape, duration_in_seconds,duration_in_hours_per_minute,comments, date_posted, latitude, longitude) in csr:
        save = {}
        save["id"] = id;
        save["datetime"] = datetime.strftime("%d-%b-%Y (%H:%M:%S.%f)");
        save["city"]=city;
        save["state"]=state;
        save["country"]=country;
        save["shape"]=shape;
        save["duration_in_seconds"]=duration_in_seconds;
        save["duration_in_hours_per_minute"]=duration_in_hours_per_minute;
        save["comments"]=comments;
        save["date_posted"]=date_posted.strftime("%d-%b-%Y");
        save["latitude"]=latitude;
        save["longitude"]=longitude;
        data.append(save)

    csr.close()
    response = json.dumps(data)
    return response

@app.route('/ufo', methods=['POST'])
def add_ufo():
    request_json = request.json
    ufo_datetime = request_json["datetime"]
    ufo_city = request_json["city"]
    ufo_state = request_json["state"]
    ufo_country = request_json["country"]
    ufo_shape = request_json["shape"]
    ufo_duration_in_seconds = request_json["duration_in_seconds"]
    ufo_duration_in_hours_per_minute = request_json["duration_in_hours_per_minute"]
    ufo_comments = request_json["comments"]
    ufo_date_posted = request_json["date_posted"]
    ufo_latitude = request_json["latitude"]
    ufo_longitude = request_json["longitude"]

    csr = db.cursor()
    csr.execute("insert into ufo_data (`datetime`,`city`,`state`,`country`,`shape`,`duration_in_seconds`,`duration_in_hours_per_minute`,`comments`,`date_posted`,`latitude`,`longitude`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (ufo_datetime,ufo_city,ufo_state,ufo_country,ufo_shape,ufo_duration_in_seconds,ufo_duration_in_hours_per_minute,ufo_comments,ufo_date_posted,ufo_latitude,ufo_longitude))
    db.commit()
    csr.close()
    response = jsonify('Ufo Added!')
    response.status_code = 200
    return response

@app.route('/ufo/<ufo_id>', methods=['PUT'])
def update_ufo(ufo_id):
    request_json = request.json
    ufo_city = request_json["city"]
    ufo_state = request_json["state"]
    ufo_country = request_json["country"]
    ufo_shape = request_json["shape"]

    csr = db.cursor()
    csr.execute("update ufo_data set city = %s, state = %s, country = %s, shape = %s where id=%s", (ufo_city,ufo_state,ufo_country,ufo_shape,ufo_id))
    db.commit()
    csr.close()

    response = jsonify('Ufo Updated')
    response.status_code = 200
    return response

@app.route('/ufo/<id>', methods=['DELETE'])
def delete_ufo(id):

    csr = db.cursor()
    csr.execute("delete from ufo_data where id="+str(id))
    db.commit()
    csr.close()
    response = jsonify('Ufo Deleted')
    response.status_code = 200
    return response


if __name__ == "__main__":
    app.run()