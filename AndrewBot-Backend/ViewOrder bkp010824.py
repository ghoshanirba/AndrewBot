import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

GET_ORDER_API_URL = "http://127.0.0.1:5001/getorder"

@app.route("/vieworder", methods=["GET"])

def view_order():
    orderID = request.args.get("orderID")
    print("Within ViewOrder.py, orderID:", orderID)
    
    #Remove leading and trailing quotes since orderID was stored in local storage.
    if orderID.startswith('"') and orderID.endswith('"'):
        orderID = orderID[1 : -1]
        
    if not orderID:
        return jsonify({"error": "orderID is required"}), 400
    
    try:
        #Call the getOrder API
        response = requests.get(f"{GET_ORDER_API_URL}/{orderID}")
        response.raise_for_status()
        order_data = response.json()
        # print(order_data)
        return jsonify(order_data), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

