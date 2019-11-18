from flask import Flask
from flask_pymongo import PyMongo
from flask import jsonify, request
from bson.json_util import dumps
from bson.objectid import ObjectId


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo-admin:password@192.168.16.23:27017/ufo?authSource=admin"
mongo = PyMongo(app, retryWrites=False)

@app.route('/ufo', methods = ['GET'])
def get_ufo():
    ufo = mongo.db.ufoCollection.find().limit(2)
    response = dumps(ufo)
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
    ufo_date_posted = request_json["date posted"]
    ufo_latitude = request_json["latitude"]
    ufo_longitude = request_json["longitude"]

    ufo_insert = mongo.db.ufoCollection.insert({
        'datetime':ufo_datetime,
        'city':ufo_city,
        'state':ufo_state,
        'country':ufo_country,
        'shape':ufo_shape,
        'duration_in_seconds':ufo_duration_in_seconds,
        'duration_in_hours_per_minute':ufo_duration_in_hours_per_minute,
        'comments':ufo_comments,
        'date posted':ufo_date_posted,
        'latitude':ufo_latitude,
        'longitude':ufo_longitude
    })

    response = jsonify('Ufo Added! new id ={}'.format(ufo_insert))
    response.status_code = 200
    return response

@app.route('/ufo/<id>', methods=['PUT'])
def update_ufo(id):
    request_json = request.json
    ufo_id = request_json["_id"]
    ufo_datetime = request_json["datetime"]
    ufo_city = request_json["city"]
    ufo_state = request_json["state"]
    ufo_country = request_json["country"]
    ufo_shape = request_json["shape"]
    ufo_duration_in_seconds = request_json["duration_in_seconds"]
    ufo_duration_in_hours_per_minute = request_json["duration_in_hours_per_minute"]
    ufo_comments = request_json["comments"]
    ufo_date_posted = request_json["date posted"]
    ufo_latitude = request_json["latitude"]
    ufo_longitude = request_json["longitude"]

    mongo.db.ufoCollection.update_one(
        {'_id': ObjectId(ufo_id['$oid']) if '$oid' in ufo_id else ObjectId(ufo_id)},
        {
            '$set' : {
                'datetime':ufo_datetime,
                'city':ufo_city,
                'state':ufo_state,
                'country':ufo_country,
                'shape':ufo_shape,
                'duration_in_seconds':ufo_duration_in_seconds,
                'duration_in_hours_per_minute':ufo_duration_in_hours_per_minute,
                'comments':ufo_comments,
                'date posted':ufo_date_posted,
                'latitude':ufo_latitude,
                'longitude':ufo_longitude
            }
        }
    )

    response = jsonify('Ufo Updated with id ={}'.format(ufo_id))
    response.status_code = 200
    return response

@app.route('/ufo/<id>', methods=['DELETE'])
def delete_ufo(id):
    mongo.db.ufoCollection.delete_one({'_id': ObjectId(id)})
    response = jsonify('Ufo Deleted with id ={}'.format(id))
    response.status_code = 200
    return response
  
@app.route('/ufo/count', methods=['GET'])
def count():
    count_ufo = mongo.db.ufoCollection.aggregate([
        {
            "$group": {
                "_id":"$shape",
                "count":{"$sum":1}
            }
        }
    ])
    response = dumps(count_ufo)
    return response
    
@app.route("/ufo/max", methods=["GET"])
def avg():
    avg_ufo = mongo.db.ufoCollection.aggregate([
        {
            "$group": {
                "_id":"$shape",
                "max_seconds":{"$max":"$duration_in_seconds"}
            }
        }
    ])
    response = dumps(avg_ufo)
    return response

if __name__ == "__main__":
    app.run()