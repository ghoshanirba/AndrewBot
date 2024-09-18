import json
import re
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from pymongo import MongoClient
import sqlite3
import openai
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB Atlas connection details
MONGO_URI = "mongodb+srv://ghoshanirba:Xy1EGbmjh3oYJC2r@cluster0.y5lid8k.mongodb.net/"
DATABASE_NAME = "AndrewBot"
COLLECTION_NAME = "Orders"

# SQLite connection details
SQLITE_DATABASE_FILE = "./SQLiteDatabases/AndrewBotDB.db"

# Initialize MongoDB Client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
orders_collection = db[COLLECTION_NAME]

# OpenAI API key (ensure to set your API key securely)
openai.api_key = "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"


def get_products_details():
    # Get all the details about products from Products SQLite table, database AndrewBotDB
    SQL_QUERY = """
                SELECT 
                    ProductID, 
                    MainCategory, 
                    SubCategory1, 
                    SubCategory2, 
                    ProductName, 
                    Brand, 
                    Weight, 
                    WeightUnits, 
                    StockInHand, 
                    MRP, 
                    DiscountPercentage 
                FROM Products
                """

    conn = sqlite3.connect(SQLITE_DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c1_cursor = conn.cursor()
    result = c1_cursor.execute(SQL_QUERY)

    rows = result.fetchall()
    json_data_products = [dict(row) for row in rows]
    return json.dumps(json_data_products, indent=4)


def match_order_with_products_inventory():
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!!! How are you?"}],
    )
    print(completion)
    print(completion.choices[0].message)
    # return(completion.choices[0].message)

#Function to convert order details from text to JSON format having 4 keys - item, brand, weight 
# and weightUnits.
def destructure_order_details(order_details):
    order_details = order_details

    user_message = (
        f'Please parse the order - "{order_details}" and provide an output '
        "in JSON format having 4 keys - item, brand, weight and weightUnits."
    )

    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": "You are an helpful assistant who helps to parse order "
                "details into JSON format from an input text.",
            },
            {
                "role": "user", 
                "content": [
                                {
                                    "type": "text", 
                                    "text": user_message
                                }
                            ]
            },
        ]
    )
   
    # Extract the content from the response
    chatGPT_response = completion.choices[0].message.content
    print("ChatH GPT Response:", chatGPT_response)
    
    try:
        # Parse the JSON response, the JSON output from chatGPT has a key "order"
        parsed_response = json.loads(chatGPT_response)
        
        # Extract the JSON content under the "order" key
        order_details_json = parsed_response.get("order",[])
        return order_details_json
    
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return []
    
    #use a regular expression to extract the JSON content.
    #returns a Match object if it finds a match, or None if no match is found.
    #A JSON body can span across multiple lines. re.DOTALL scans if the JSON body is in new/multiple lines
    # insted of being present only in 1 line.
    # json_match = re.search(r'\[.*\]', chatGPT_response, re.DOTALL)
    
    # if json_match:
    #     # Extract JSON string from the match object. group(0) contains the entire matched portion of
    #     # the JSON body.
    #     json_string = json_match.group(0)
        
    #     try:
    #         # Parse the JSON string to verify that the JSON body is good.
    #         parsed_json = json.loads(json_string)
    #         return(parsed_json)
    #     except json.JSONDecodeError as e:
    #         print("Failed to decode JSON:", e)
    # else:
    #     print("JSON body not found in the response.")


def retrieve_embedding(order_details_embeddings):
    
    order_details_embeddings = order_details_embeddings

    with open("product_embeddings.pkl", "rb") as f:
        data = pickle.load(f)  # the data is a dictionay having 3 keys - ProductKeys, Embeddings and Descriptions
        # print("data type:", type(data))
        # print("data embedding type:", type(data["Embeddings"]))     #Embeddings is (50 X 384) 2D array
        # print("data embedding shape", np.array(data["Embeddings"]).shape)

    stored_embeddings = data["Embeddings"]
    product_keys = data["ProductKeys"]
    descriptions = data["Descriptions"]
    
    #calculate cosine similarities between order_details_embeddings and stored_embeddings
    similarities = cosine_similarity(order_details_embeddings, stored_embeddings)
    print("similarities:", similarities)
    
    #Find the index of the best match for each order detail
    best_match_indices = np.argmax(similarities, axis=1)
    print("best_match_indices", best_match_indices)
    
    # Retrieve the best matching product keys and descriptions
    best_product_keys = [product_keys[index] for index in best_match_indices]
    best_descriptions = [descriptions[index] for index in best_match_indices]

    return best_product_keys, best_descriptions


@app.route("/health", methods=["GET"])
def get_health():
    return "Ok"


@app.route("/orders", methods=["POST"])
def create_order():
    print("Within OrderManagementAPI.py create order")

    data = request.json
    order_details = data.get("orderDetails")
    print("order_details:", order_details)

    order_details_json = destructure_order_details(order_details)
    print("Parsed JSON:", json.dumps(order_details_json, indent=4))
    order_details_df = pd.DataFrame(order_details_json) #order_details_df will contain indexes - 0, 1, 2 etc in the beginning
    print("order_details_df")
    print(order_details_df)
    
    #Convert the order details into embeddings
    order_details_description = order_details_df.apply(
        lambda row: f"{row['item']} | {row['brand']} | {row['weight']} | {row['weightUnits']}",
        axis=1
    )
    
    # model = SentenceTransformer("all-MiniLM-L6-v2")
    # order_details_embeddings = model.encode(order_details_description,convert_to_tensor=False)
    # print("order_details_embeddings type:", type(order_details_embeddings))
    # print("order_details_embeddings shape:", order_details_embeddings.shape)
    # #----------------------------------------------------------------#
    
    # best_product_keys, best_descriptions = retrieve_embedding(order_details_embeddings)
    
    # print("Best Matching Product Keys:", best_product_keys)
    # print("Best Matching Descriptions:", best_descriptions)
    
    # Example usage
    # embedding, description = retrieve_embedding(
    #     "Atta with Multigrains - High Fibre", "Aashirvaad", "5", "Kg"
    # )
    # if embedding is not None:
    #     print("Retrieved embedding 1:", embedding)
    #     print("Original Input Description:", description)
        # Access individual values in the embedding
        # for i, value in enumerate(embedding):
        #     print(f"Dimension {i}: {value}")

    # Example usage
    # embedding, description = retrieve_embedding(
    #     "Maida/Refined Flour", "Fortune", "5", "Kg"
    # )
    # if embedding is not None:
    #     print("Retrieved embedding 2:", embedding)
    #     print("Original Input Description:", description)

    # embedding, description = retrieve_embedding(
    #     "Atta/Godihittu - Whole Wheat", "Aashirvaad", "5", "Kg"
    # )
    # if embedding is not None:
    #     print("Retrieved embedding 3:", embedding)
    #     print("Original Input Description:", description)
        # Access individual values in the embedding

    # json_result_products = get_products_details()

    # print(json_result_products)
    # match_order_with_products_inventory()
    # print("openAIOutput:", openAIOutput)
    return "Ok"


@app.route("/orders", methods=["GET"])
def get_order():
    orderID = request.args.get("orderID")
    print("Within OrderManagementAPI.py view order, orderID:", orderID)

    # Remove leading and trailing quotes since orderID was stored in local storage.
    try:
        if orderID.startswith('"') and orderID.endswith('"'):
            orderID = orderID[1:-1]
        orderID = int(orderID)
    except ValueError:
        return jsonify({"error": "Invalid order ID format"}), 400

    try:
        # Fetch the order details using orderID from MongoDB
        order = orders_collection.find_one({"orderID": orderID})

        if order:
            # Convert MongoDB object to JSON
            print(order["_id"])
            order["_id"] = str(order["_id"])  # Convert ObjectId to string
            order_json = json.dumps(order, indent=4)
            # print("Order JSON from MongoDB:", order_json)
            return jsonify(order), 200
        else:
            return jsonify({"error": "Order not found"}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
