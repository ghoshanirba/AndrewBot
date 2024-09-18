import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB Atlas connection details
MONGO_URI = "mongodb+srv://ghoshanirba:Xy1EGbmjh3oYJC2r@cluster0.y5lid8k.mongodb.net/"
DATABASE_NAME = "AndrewBot"
COLLECTION_NAME = "Orders"

#Initialize MongoDB Client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
orders_collection = db[COLLECTION_NAME]

@app.route("/health", methods=["GET"])
def get_health():
    return("Ok")

@app.route("/getorder/<orderID>", methods=["GET"])
def get_order(orderID):
    print("Within GetOrder.py, orderID:", orderID)
    orderID=int(orderID)
    
    try:
        #Fetch the order using orderID
        order = orders_collection.find_one({"orderID" : orderID})
        if order:
            # Convert MongoDB object to JSON
            print(order['_id'])
            order['_id'] = str(order['_id'])  # Convert ObjectId to string
            order_json = json.dumps(order, indent=4)
            # print("Order JSON from MongoDB:", order_json)
            return jsonify(order), 200
        else:
            return jsonify({"error": "Order not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__': 
   app.run(host='0.0.0.0', port=5001, debug=True)  
 
