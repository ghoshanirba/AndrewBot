import json
from flask import Flask, jsonify, request
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/createorder", methods=["PUT"])

def create_order():
    print("within create order CreateOrder.py")
    
