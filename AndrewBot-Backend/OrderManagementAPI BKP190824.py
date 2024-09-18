import json
import pickle
from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import pandas as pd
import requests
from pymongo import MongoClient
import sqlite3
import openai
import re
from sentence_transformers import SentenceTransformer
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


def get_product_details(productID):
    print("get_product_details")
    print("productID:", productID)
    print("productID type", type(productID))
    # open database connection
    conn = sqlite3.connect(SQLITE_DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c1_cursor = conn.cursor()

    # Get all the details about products from Products SQLite table, database AndrewBotDB
    SQL_QUERY = """
                SELECT 
                     Product_ID
                    ,Product_Name
                    ,Weight
                    ,MRP
                    ,Selling_Price
                    ,Discount
                    ,Brand
                    ,Stock_In_Hand
                FROM Products
                WHERE
                    Product_ID = ?
                """

    result = c1_cursor.execute(SQL_QUERY, (productID,))

    row = result.fetchone()
    print("row:", row)
    conn.close()

    # Check if any data is retrieved
    if not row:
        print(f"No matching product found with product ID {productID}.")
        return None
    else:
        product_details = dict(row)
        return product_details


# Function to convert order details from text to JSON format having 4 keys - item, brand, weight
# and weightUnits.
def destructure_order_details(order_details):
    order_details = order_details

    user_message = (
        f'Please parse the order - "{order_details}" and provide an output '
        "in JSON format having 4 keys - item, brand, weight and weightUnits. "
        "If any specific attribute is passed in the item then add it with the item key itself. "
        "Default value of item, brand, weight and weightUnits is N.A. "
        "Assign default values whenever one of the key value pairs have not been obtained."
    )

    # completion = openai.chat.completions.create(
    #     model="gpt-4o-mini",
    #     response_format={ "type": "json_object" },
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "You are an helpful assistant who helps to parse order "
    #             "details into JSON format from an input text. Send a default response as "
    #             "I do not understand, please pass an order, if anything else other than an order is"
    #             "passed.",
    #         },
    #         {
    #             "role": "user",
    #             "content": [
    #                             {
    #                                 "type": "text",
    #                                 "text": user_message
    #                             }
    #                         ]
    #         },
    #     ]
    # )

    # # Extract the content from the response
    # chatGPT_response = str(completion.choices[0].message.content)

    chatGPT_response = {
        "order": [
            {
                "item": "cold drinks",
                "brand": "mirinda",
                "weight": "1",
                "weightUnits": "L",
            },
            {"item": "wheat", "brand": "ashirbaad", "weight": "5", "weightUnits": "kg"},
            {"item": "chatu", "brand": "mana", "weight": "200", "weightUnits": "grams"},
            {
                "item": "rice flour",
                "brand": "bb royal",
                "weight": "100",
                "weightUnits": "gms",
            },
        ]
    }
    print("Chat GPT Response:", chatGPT_response)

    try:
        # Parse the JSON response, the JSON output from chatGPT has a key "order"
        parsed_response = chatGPT_response
        # parsed_response = json.loads(chatGPT_response)

        # Extract the JSON content under the "order" key. If the key doesn't exist,
        # it returns an empty list [].
        order_details_json = parsed_response.get("order", [])
        return order_details_json

    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return []


def standardize_weight_units(weight_units):
    weight_units = weight_units.lower()

    standardization_weight_units_map = {
        "kg": "kg",
        "kgs": "kg",
        "kilogram": "kg",
        "kilograms": "kg",
        "gm": "gm",
        "gms": "gm",
        "gram": "gm",
        "grams": "gm",
        "ltr": "ltr",
        "ltrs": "ltr",
        "litre": "ltr",
        "litres": "ltr",
        "liter": "ltr",
        "liters": "ltr",
        "kilo": "kg",
        "kilos": "kg",
        "kilo gram": "kg",
        "kilo grams": "kg",
    }

    if weight_units in standardization_weight_units_map:
        return standardization_weight_units_map.get(weight_units)
    else:
        return weight_units


def open_pickle_files(filename):
    try:
        f1 = open(filename, "rb")
        print("pickle files opened.")
        return f1
    except FileNotFoundError:
        print(f"ERROR: The file {filename} was not found during opening it.")
    except FileExistsError:
        print(f"ERROR: The file {filename} does not exist during opening.")
    except IOError:
        print(f"ERROR: IOError occurred while opening the file {filename}.")
    except Exception as e:
        print(f"An unexpected error occurred while opening the file {filename}.")


def close_pickle_files(filename):
    try:
        filename.close()
        print("pickle files closed.")
    except ValueError:
        print(
            f"ERROR: The file {filename} is already closed or is not a valid file object."
        )
    except IOError:
        print(f"ERROR: IOError occurred while closing the file {filename}.")
    except Exception as e:
        print(f"An unexpected error occurred while closing the file {filename}.")


def load_embeddings(fileObj):
    embeddings_list = []
    try:
        while True:
            embeddings_list.append(pickle.load(fileObj))
    except EOFError:
        pass

    embeddings_df = pd.concat(embeddings_list, ignore_index=True)

    return embeddings_df


def get_order_details_request():
    print("get_order_details_request")
    data = request.json
    print("data:", data)
    if data is None:
        print("ERROR: No JSON data found in the user request.")
        return None

    order_details = data.get("orderDetails", "").strip().lower()

    # Regular expression to match any character that is not a letter, digit, comma, or space
    # order_details_cleaned = re.sub(r'[^\w\s,\-()\/+&\'\"]', '', order_details)
    # print("order_details_cleaned:", order_details_cleaned)

    # return(order_details_cleaned)

    print("order_details:", order_details)

    return order_details


def clean_input_string(input_text, allowable_chars, replacement_char):
    input_text = str(input_text).strip().lower()
    # Create a regex pattern that matches any character not in the allowable_chars list
    # Escape special characters to avoid regex errors
    escaped_allowable_chars = re.escape(allowable_chars)
    pattern = r"[^a-zA-Z0-9" + escaped_allowable_chars + r"\s]"

    # # Replace disallowed characters with the replacement_char
    text = re.sub(pattern, replacement_char, input_text)

    # Remove extra spaces that might have been introduced in between words
    cleaned_text = re.sub(r"\s+", " ", text).strip().lower()

    return cleaned_text


def process_user_request_brand(
    user_request_brand_name, model, brand_name_embeddings_df
):
    allowable_chars_brand_name = "&"
    replacement_char_brand_name = " "

    user_request_brand_cleaned = clean_input_string(
        user_request_brand_name, allowable_chars_brand_name, replacement_char_brand_name
    )

    user_request_brand_embedding = model.encode(user_request_brand_cleaned)

    best_matched_brand_name = find_closest_matched_brand_name(
        user_request_brand_embedding, brand_name_embeddings_df
    )

    return best_matched_brand_name


def process_product_name(user_request_product_name, model, product_name_embeddings_df):
    allowable_chars_product_name = "&%"
    replacement_char_product_name = " "

    user_request_product_name_cleaned = clean_input_string(
        user_request_product_name,
        allowable_chars_product_name,
        replacement_char_product_name,
    )

    input_text = f"The product is named {user_request_product_name_cleaned}."
    input_text = input_text.lower()
    print("input:", input_text)

    user_request_product_name_embedding = model.encode(
        user_request_product_name_cleaned
    )

    best_matched_product_id, best_matched_product_name = (
        find_closest_matched_product_name(
            user_request_product_name_embedding, product_name_embeddings_df
        )
    )

    return best_matched_product_id, best_matched_product_name


def process_product(
    user_request_product_name,
    best_matched_brand_name,
    user_request_product_weight,
    user_request_product_weight_unit,
    model,
    product_embeddings_df,
):
    allowable_chars_product_name = "&%"
    replacement_char_product_name = " "
    allowable_chars_category = "&"
    replacement_char_category = " "
    allowable_chars_brand_name = "&"
    replacement_char_brand_name = " "

    user_request_product_name_cleaned = clean_input_string(
        user_request_product_name,
        allowable_chars_product_name,
        replacement_char_product_name,
    )
    best_matched_brand_name_cleaned = clean_input_string(
        best_matched_brand_name, allowable_chars_brand_name, replacement_char_brand_name
    )

    input_text = f"The product is named {user_request_product_name_cleaned}. It belongs to the brand {best_matched_brand_name_cleaned}. "

    input_text = input_text.lower()
    print("input:", input_text)

    user_request_product_embedding = generate_embedding(input_text, model)

    # do a look up in the Products embedding file to find the best matched product ID.
    best_matched_productID = find_closest_matched_product_ID(
        user_request_product_embedding, product_embeddings_df
    )

    return best_matched_productID


def generate_embedding(input_text, model):
    embedding = model.encode(input_text)
    return embedding


def find_closest_matched_brand_name(
    user_request_brand_embedding, unique_brandName_embeddings_df
):
    unique_brandName_embeddings_df_len = len(unique_brandName_embeddings_df)

    print("unique_brandName_embeddings_df len:", unique_brandName_embeddings_df_len)

    user_request_brand_embedding_array = np.array(
        user_request_brand_embedding.tolist()
    ).reshape(1, -1)

    unique_brandName_embeddings_array = np.array(
        unique_brandName_embeddings_df["brandEmbedding"].tolist()
    ).reshape(unique_brandName_embeddings_df_len, -1)

    similarities = cosine_similarity(
        user_request_brand_embedding_array, unique_brandName_embeddings_array
    )[0]
    best_matched_index = np.argmax(similarities)
    best_matched_brand_name = unique_brandName_embeddings_df["Brand"][
        best_matched_index
    ]

    return best_matched_brand_name


def find_closest_matched_product_name(
    user_request_product_name_embedding, product_name_embeddings_df
):
    best_matched_product_name = " "
    product_name_embeddings_df_len = len(product_name_embeddings_df)
    print("product_name_embeddings_df_len:", product_name_embeddings_df_len)

    user_request_product_name_embedding_array = np.array(
        user_request_product_name_embedding.tolist()
    ).reshape(1, -1)

    product_name_embeddings = np.array(
        product_name_embeddings_df["nameEmbedding"].tolist()
    ).reshape(product_name_embeddings_df_len, -1)

    similarities = cosine_similarity(
        user_request_product_name_embedding_array, product_name_embeddings
    )[0]
    best_matched_index = np.argmax(similarities)
    best_matched_product_id = product_name_embeddings_df["productID"][
        best_matched_index
    ]

    product_details = get_product_details(int(best_matched_product_id))

    if product_details is not None:
        best_matched_product_name = product_details["Product_Name"]

    return best_matched_product_id, best_matched_product_name


def find_closest_matched_product_ID(
    user_request_product_embedding, product_embeddings_df
):
    product_embeddings_df_len = len(product_embeddings_df)
    print("product_embeddings_df_len:", product_embeddings_df_len)
    user_product_embedding_array = np.array(
        user_request_product_embedding.tolist()
    ).reshape(1, -1)
    all_product_embeddings = np.array(
        product_embeddings_df["embedding"].tolist()
    ).reshape(product_embeddings_df_len, -1)

    similarities = cosine_similarity(
        user_product_embedding_array, all_product_embeddings
    )[0]
    best_matched_index = np.argmax(similarities)
    best_matched_product_id = product_embeddings_df["productID"][best_matched_index]

    return best_matched_product_id


@app.route("/health", methods=["GET"])
def get_health():
    return "Ok"


@app.route("/orders", methods=["POST"])
def create_order():
    print("Within OrderManagementAPI.py create order")
    all_products_info = []
    brand_name_embeddings_file_path = "brand_name_embeddings.pkl"
    product_name_embeddings_file_path = "product_name_embeddings.pkl"
    product_embeddings_file_path = "product_embeddings.pkl"

    # Open pickle files
    brand_name_embeddings_file_obj = open_pickle_files(brand_name_embeddings_file_path)
    product_name_embeddings_file_obj = open_pickle_files(
        product_name_embeddings_file_path
    )
    product_embeddings_file_obj = open_pickle_files(product_embeddings_file_path)

    if (
        (brand_name_embeddings_file_obj is None)
        or (product_name_embeddings_file_obj is None)
        or (product_embeddings_file_obj is None)
    ):
        print("Failed to open the pickle file, exiting the program.")
        return "ERROR: Could Not Open Pickle Files."
    else:
        brand_name_embeddings_df = load_embeddings(brand_name_embeddings_file_obj)
        product_name_embeddings_df = load_embeddings(product_name_embeddings_file_obj)
        product_embeddings_df = load_embeddings(product_embeddings_file_obj)
        close_pickle_files(product_embeddings_file_obj)

        # get the order details that the customer has requested.
        order_details = get_order_details_request()
        order_details_json = destructure_order_details(order_details)

        # Load RoBerta model.
        model = SentenceTransformer("roberta-base-nli-stsb-mean-tokens")

        # Process for each product
        for product in order_details_json:
            print("product:", product)
            user_request_product_name = str(product.get("item")).strip().lower()
            user_request_brand_name = str(product.get("brand")).strip().lower()
            user_request_product_weight = str(product.get("weight")).strip().lower()
            user_request_product_weight_unit = (
                str(product.get("weightUnits")).strip().lower()
            )

            # Determine the best matched brand name as per user request
            best_matched_brand_name = process_user_request_brand(
                user_request_brand_name, model, brand_name_embeddings_df
            )

            print("best_matched_brand_name:", best_matched_brand_name)

            # Find best matched prodcut name
            best_matched_product_name_id, best_matched_product_name = (
                process_product_name(
                    user_request_product_name, model, product_name_embeddings_df
                )
            )

            print("best_matched_product_name_id:", best_matched_product_name_id)
            print("best_matched_product_name:", best_matched_product_name)

            # Find best matched product ID
            best_matched_productID = process_product(
                user_request_product_name,
                best_matched_brand_name,
                user_request_product_weight,
                user_request_product_weight_unit,
                model,
                product_embeddings_df,
            )

            print("productID:", best_matched_productID)
            print("productID type:", type(best_matched_productID))
            # use the product ID to get the product details from Products table.
            product_details = get_product_details(int(best_matched_productID))
            print("product_details:", product_details)
            if product_details:
                all_products_info.append(product_details)

    return all_products_info


@app.route("/orders", methods=["GET"])
def get_order():
    orderID = str(request.args.get("orderID"))
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
