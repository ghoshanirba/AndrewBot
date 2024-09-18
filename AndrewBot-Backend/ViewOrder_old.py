import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/", methods=["GET"])
def get_order():
    
    orders = {
    
            "orderID": 100002,
            "userID": "ghoshanirban",
            "items": [
                {
                    "productID": 1,
                    "productName": "wheat",
                    "productBrand": "aashirvad",
                    "productWeight": "5kg",
                    "productQty": 1,
                },
                {
                    "productID": 2,
                    "productName": "rice",
                    "productBrand": "india gate",
                    "productWeight": "2kg",
                    "productQty": 2,
                },
                {
                    "productID": 3,
                    "productName": "turmeric",
                    "productBrand": "sunrise",
                    "productWeight": "200gm",
                    "productQty": 3,
                },
            ],
            "orderConfirmedByUser":"Y",
            "orderCreateDate": datetime.now().isoformat(),
            "rowUpdateTimestamp": datetime.now().isoformat(),
        }
    print(json.dumps(orders, indent=4))  # Print the JSON to confirm the structure
    #return jsonify(orders)
    if order_number in orders:
        return jsonify(orders)
    else:
        return jsonify({"error": f"Order with orderID {order_number} not found"}), 404
