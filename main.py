from flask import Flask, request, jsonify, json, redirect, url_for
from flask_pymongo import PyMongo
from marshmallow import Schema, fields, ValidationError
from bson.json_util import dumps
from json import loads

from flask_cors import CORS #for testing 

#adding time stuff
from pytz import datetime
import pytz

app = Flask(__name__)
CORS(app) #for testing

app.config["MONGO_URI"] = ""
mongo = PyMongo(app)

#global dictionary to store information about a single user 
userData = {}


#add datavalidation class
class TankValidation(Schema):
    location = fields.String(required = True)
    lat = fields.String(required = True)
    long = fields.String(required = True)
    percentage_full = fields.Integer(required = True)
     
#Data Routes 
@app.route("/data")
def data_get():
    tanks = mongo.db.tanks.find()
    # A find will return an array of objects, to convert it into a json object, do the following
    return jsonify(loads(dumps(tanks)))

@app.route("/data", methods = ["POST"])
def data_post():
    try:
        tankTemp = TankValidation().load(request.json)
        tankTemp_id = mongo.db.tanks.insert_one(tankTemp).inserted_id
        retTank = mongo.db.tanks.find_one(tankTemp_id)
        return loads(dumps(retTank)) #no need to jsonify since its a single object. Only jsonify when a list of objects are returned
    except ValidationError as ve:
        return ve.messages, 400


@app.route('/data/<ObjectId:id>', methods = ["PATCH"])
def data_patch(id):
    mongo.db.tanks.update_one({"_id": id},{"$set": request.json})
    patchedTank = mongo.db.tanks.find_one(id)
    return loads(dumps(patchedTank))
        
@app.route('/data/<ObjectId:id>', methods = ["DELETE"])
def data_delete(id):
    result = mongo.db.tanks.delete_one({"_id":id})
    if result.deleted_count == 1:
        successDict = { "success":True,}
        return jsonify(successDict) 
    else:
        successDict = { "success":False}
        return jsonify(successDict), 400

#Profile  Routes 
@app.route('/profile')
def profile_get():
    global userData
    successDict = {
        "success" :True,
        "data" : userData
    }
    return jsonify(successDict)

@app.route('/profile', methods = ['POST'])
def profile_post():
    #obtain time stamp
    tVar = datetime.datetime.now(tz=pytz.timezone('America/Jamaica'))
    tVartoString = tVar.isoformat()
    #obtain json object from the request object
    userD = request.json
    #do the validation 
    if len(userD) > 0:
        #update global dictionary to show that a user has logged in
        global userData
        userData = userD
        #append time stamp to local dictionary and prepare for return
        userD["last_updated"] = tVartoString
        successDict = {
            "successs":True,
            "data": userD
        }
        return jsonify(successDict)
    else:
        return redirect(url_for("profile_get"))

@app.route('/profile', methods = ["PATCH"])
def profile_patch():
    global userData #this global variable will be updated locally
    #obtain time stamp
    tVar = datetime.datetime.now(tz=pytz.timezone('America/Jamaica'))
    tVartoString = tVar.isoformat()
    #obtain json object from the request object in a local dictionary
    userD = request.json   
    #user can only patch if the profile has already been created
    #Therefore, check if global dictionary has an element
    if len(userData) > 0:
        #patch global dictionary
        userData = userD
        #append time stamp to local dictionary and prepare for return
        userD["last_updated"] = tVartoString
        successDict = {
        "successs":True,
        "data": userD
        }            
        return jsonify(successDict)
    else:
        return redirect(url_for("profile_get"))


if __name__ == "__main__":
    app.run(debug = True)

