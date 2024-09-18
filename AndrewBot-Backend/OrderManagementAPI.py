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
from scipy.stats import pearsonr, spearmanr, kendalltau
from scipy.spatial.distance import euclidean, cityblock
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the Environment Variables
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
MONGO_DB_PATH = os.getenv("MONGO_DB_PATH")

# MongoDB Atlas connection details
MONGO_URI = MONGO_DB_PATH
DATABASE_NAME = "AndrewBot"
COLLECTION_NAME = "Orders"

#  Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
orders_collection = db[COLLECTION_NAME]

# SQLite connection details
SQLITE_DATABASE_FILE = "./SQLiteDatabases/AndrewBotDB.db"

# Set the OpenAI API key
openai.api_key = OPEN_AI_API_KEY


def get_product_details(productID):
    # print("get_product_details")
    # print("productID:", productID)
    # print("productID type", type(productID))
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
                    ,Magnitude
                    ,Magnitude_Unit
                    ,MRP
                    ,Selling_Price
                    ,Discount
                    ,Brand
                    ,Stock_In_Hand
                    ,Main_Category
                    ,Sub_Category1
                    ,Sub_Category2
                FROM Products
                WHERE
                    Product_ID = ?
                """

    result = c1_cursor.execute(SQL_QUERY, (productID,))

    row = result.fetchone()
    # print("row:", row)
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
####################################################################################    
#  UNCOMMENT BELOW TO MAKE OPEN AI API CALL ACTIVE
    user_message = (
        f'Please parse the order - "{order_details}" and provide an output '
        'in JSON format having 4 keys - item, brand, weight and weightUnits. '
        'Wrap the output in a main key "order" and prepare a list.'
    )

    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": "You are an helpful assistant who helps to parse order "
                "details into JSON format from an input text. Send a default response as "
                "I do not understand, please pass an order, if anything else other than an order is"
                "passed."
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
        ],
        temperature=0,
        top_p=0
        
    )

    # # # Extract the content from the response
    chatGPT_response = str(completion.choices[0].message.content)
# UNCOMMENT ABOVE FOR OPEN AI API CALL
#######################################################################################
    # chatGPT_response = {
    #     "order": [
    #         {
    #             "item": "cold drinks",
    #             "brand": "mirinda",
    #             "weight": "250",
    #             "weightUnits": "ml",
    #         },
    #         {
    #             "item": "whole wheat atta",
    #             "brand": "ashirbaad",
    #             "weight": "5",
    #             "weightUnits": "kg",
    #         },
            # {"item": "wheat", "brand": "pilsbury", "weight": "5", "weightUnits": "kilo"},
            # {"item": "sattu", "brand": "mana", "weight": "200", "weightUnits": "grams"},
            # {
            #     "item": "rice flour",
            #     "brand": "bb royal",
            #     "weight": "100",
            #     "weightUnits": "gms",
            # },
            # {
            #     "item": "Tea",
            #     "brand": "Tata Tea Premium",
            #     "weight": "250",
            #     "weightUnits": "gms",
            # },
            # {
            #     "item": "Turmeric powder",
            #     "brand": "Everest",
            #     "weight": "500",
            #     "weightUnits": "gms",
            # },
            # {
            #     "item": "Sharbat",
            #     "brand": "mapro",
            #     "weight": "500",
            #     "weightUnits": "gms",
            # },
            # {
            #     "item": "sambar masala",
            #     "brand": "MTR",
            #     "weight": "100",
            #     "weightUnits": "gms",
            # },
            # {
            #     "item": "garam masala",
            #     "brand": "Everest",
            #     "weight": "100",
            #     "weightUnits": "gms",
            # },
            # {
            #     "item": "coconut oil",
            #     "brand": "parachute",
            #     "weight": "100",
            #     "weightUnits": "ml",
            # },
            # {
            #     "item": "khacchi ghani mustard oil",
            #     "brand": "fortune",
            #     "weight": "1",
            #     "weightUnits": "ltr",
            # },
            # {
            #     "item": "ghee",
            #     "brand": "patanjali",
            #     "weight": "1",
            #     "weightUnits": "ltr",
            # },
            # {
            #     "item": "coconut water",
            #     "brand": "fresho",
            #     "weight": "1",
            #     "weightUnits": "ltr",
            # },
    #         {
    #             "item": "seed and nut mix",
    #             "brand": "true elements",
    #             "weight": "1",
    #             "weightUnits": "ltr",
    #         },
    #     ]
    # }
    print("Chat GPT Response:", chatGPT_response)

    try:
        # Parse the JSON response, the JSON output from chatGPT has a key "order"
        # parsed_response = chatGPT_response # type: ignore
        parsed_response = json.loads(chatGPT_response)

        # Extract the JSON content under the "order" key. If the key doesn't exist,
        # it returns an empty list [].
        order_details_json = parsed_response.get("order", [])    # type: ignore
        print("order_details_json:", order_details_json)
        return order_details_json

    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return []


def standardize_weight_units(weight_units):
    weight_units = weight_units.lower()

    standardization_weight_units_map = {
        "ml" : "ml",
        "millilitre" : "ml",
        "milli litre" : "ml",
        "l" : "l",
        "ltr" : "l",
        "ltrs" : "l",
        "litre" : "l",
        "litres" : "l",
        "liter" : "l",
        "liters" : "l",
        "kg" : "kg",
        "kgs" : "kg",
        "kilogram" : "kg",
        "kilograms" : "kg",
        "kilo" : "kg",
        "kilos" : "kg",
        "kilo gram" : "kg",
        "kilo grams" : "kg",
        "gm" : "g",
        "gms" : "g",
        "gram" : "g",
        "grams" : "g",
        "pcs" : "pcs",
        "pieces" : "pcs",
        "pc" : "pc",
        "piece" : "pc",
        "pellets" : "pc",
        "plates" : "pc",
        "pallets" : "pc",
        "combo" : "combo",
        "bb combo" : "bb combo",
        "bbcombo" : "bb combo "        
    }

    if weight_units in standardization_weight_units_map:
        return standardization_weight_units_map.get(weight_units)
    else:
        return weight_units


def open_pickle_files(filename, file_open_mode):
    try:
        f1 = open(filename, file_open_mode)
        print(f"{filename} pickle file opened in {file_open_mode} mode.")
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
    # print("get_order_details_request")
    # data = request.json
    data = request.args.get('orderDetails')
    print("data:", data)
    if data is None:
        print("ERROR: No JSON data found in the user request.")
        return None

    # order_details = data.get("orderDetails", "").strip().lower()
    
    order_details = data.strip().lower()
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


def process_product(
    user_request_product_name,
    best_matched_brand_name,
    user_request_product_weight,
    user_request_product_weight_unit,
    model,
    product_embeddings_df,
    min_acceptable_cosine_similarity,
    isFirst_Time,
    top_n,
):
    allowable_chars_product_name = "&%/+,.()-\'+"
    replacement_char_product_name = " "
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

    if isFirst_Time:
        # Create embeddings for user request product name, use this as main
        input_text_product = (
            f"What is the complete product name that contains {user_request_product_name_cleaned} "
            f"and having the brand name {best_matched_brand_name_cleaned}."
        )
    else:
        # Create embeddings for user request product name, use this to do a recheck
        input_text_product = (
            f"Product name: {user_request_product_name_cleaned}. "
            f"Brand: {best_matched_brand_name_cleaned}. "
            f"{user_request_product_name_cleaned} is a popular product by {best_matched_brand_name_cleaned}. "
            f"This product is known for its quality and is widely recognized under the {best_matched_brand_name_cleaned} brand."
        )

    print("input_text_product:", input_text_product)

    user_request_product_embedding = generate_embedding(input_text_product, model)

    ################### COSINE SIMILARITIES ####################
    # do a look up in the Products embedding file to find the best matched product ID.
    # best_matched_productID = find_closest_matched_product_ID(
    #     user_request_product_embedding, product_embeddings_df
    # )

    top_matched_product_ids_with_similarity_scores = find_top_matched_product_ID(
        user_request_product_embedding,
        product_embeddings_df,
        top_n,
        min_acceptable_cosine_similarity,
        isFirst_Time,
    )

    return top_matched_product_ids_with_similarity_scores


def generate_embedding(input_text, model):
    embedding = model.encode(input_text)
    return embedding


def find_closest_matched_brand_name(
    user_request_brand_embedding, unique_brandName_embeddings_df
):
    # print("within find_closest_matched_brand_name")
    unique_brandName_embeddings_df_len = len(unique_brandName_embeddings_df)

    # print("unique_brandName_embeddings_df len:", unique_brandName_embeddings_df_len)

    user_request_brand_embedding_array = np.array(
        user_request_brand_embedding.tolist()
    ).reshape(1, -1)

    unique_brandName_embeddings_array = np.array(
        unique_brandName_embeddings_df["brandEmbedding"].tolist()
    ).reshape(unique_brandName_embeddings_df_len, -1)

    similarities = cosine_similarity(
        user_request_brand_embedding_array, unique_brandName_embeddings_array
    )[0]

    # print("similarities:", similarities)
    best_matched_index = np.argmax(similarities)
    best_matched_brand_name = unique_brandName_embeddings_df["Brand"][
        best_matched_index
    ]

    return best_matched_brand_name


def find_closest_matched_product_ID(
    user_request_product_embedding, product_embeddings_df
):
    product_embeddings_df_len = len(product_embeddings_df)
    # print("product_embeddings_df_len:", product_embeddings_df_len)
    user_request_product_embedding_array = np.array(
        user_request_product_embedding.tolist()
    ).reshape(1, -1)

    all_product_embeddings = np.array(
        product_embeddings_df["embedding"].tolist()
    ).reshape(product_embeddings_df_len, -1)

    similarities = cosine_similarity(
        user_request_product_embedding_array, all_product_embeddings
    )[0]

    best_matched_index = np.argmax(similarities)
    best_matched_product_id = product_embeddings_df["productID"][best_matched_index]

    # Get the maximum similarity value
    # print("shape of similarities:", similarities.shape)
    max_similarity = similarities[best_matched_index]
    # print("Maximum Cosine Similarity:", max_similarity)

    return best_matched_product_id


def find_top_matched_product_ID(
    user_request_product_embedding,
    product_embeddings_df,
    top_n,
    min_acceptable_cosine_similarity,
    isFirst_Time,
):
    # print("WITHIN find_top_matched_product_ID METHOD")
    top_matched_product_ids = []
    top_matched_product_ids_with_similarity_scores = []
    product_embeddings_df_len = len(product_embeddings_df)
    # print("product_embeddings_df_len:", product_embeddings_df_len)

    user_request_product_embedding_array = np.array(
        user_request_product_embedding.tolist()
    ).reshape(1, -1)

    all_product_embeddings = np.array(
        product_embeddings_df["embedding"].tolist()
    ).reshape(product_embeddings_df_len, -1)

    similarities = cosine_similarity(
        user_request_product_embedding_array, all_product_embeddings
    )[0]

    # Get indices of the top N similarities
    # top_indices = np.argsort(similarities)[::-1][:top_n]
    top_indices = np.argsort(similarities)[::-1]
    top_indices_top_n = top_indices[:top_n]

    # Get the top N product IDs
    top_matched_product_ids = (
        product_embeddings_df["productID"].iloc[top_indices_top_n].tolist()
    )

    # print("top_matched_product_ids:", top_matched_product_ids)

    # Create a list of all products whose cosine similarity score is within acceptable range.
    for index1 in top_indices:
        if similarities[index1] > min_acceptable_cosine_similarity:
            # Get the top product IDs with their similarity scores
            top_matched_product_ids_with_similarity_scores.append(
                {
                    "productID": product_embeddings_df["productID"].iloc[index1],
                    "similarityScore": similarities[index1],
                }
            )
        else:
            break

    # Create list of top N products whose cosine similarity score is less than acceptable range.
    if not top_matched_product_ids_with_similarity_scores:
        top_matched_product_ids_with_similarity_scores = [
            {
                "productID": product_embeddings_df["productID"].iloc[index2],
                "similarityScore": similarities[index2],
            }
            for index2 in top_indices_top_n
        ]

    return top_matched_product_ids_with_similarity_scores


def prepare_API_response(top_matched_productID_product_details_reordered):
    products = {}
    children = []
    children_dict = {}
    record_count = 0
    total_record_count = {}
    
    record_count = len(top_matched_productID_product_details_reordered)
    # total_record_count = dict("total_count_of_one_product_with_children" : record_count)
    #     "total_count_of_one_product_with_children" : record_count
        
    
    for index, product in enumerate(top_matched_productID_product_details_reordered):
        keep_selected_yes_or_no = "Y" if index == 0 else "N"
        product_details = extract_product_details(product, keep_selected_yes_or_no)
        
        if index == 0:
           products.update(product_details)
        else:
           children.append(product_details)
           
        if children:
            products["children"] = children
            
    products["total_count_of_one_product_with_children"] = record_count
        # record_count += 1
        # if record_count == 1:
        #     keep_selected_yes_or_no = "Y"            
        #     product_details = extract_product_details(product, keep_selected_yes_or_no)
        #     products.append(product_details)
        # else:
        #     keep_selected_yes_or_no = "N"
        #     product_details = extract_product_details(product, keep_selected_yes_or_no)
        #     children.append(product_details)   
        
        # children_dict["children"] = children
        # products.append(children_dict)
        # products.append(total_record_count)
        # total_record_count["total_count_of_one_product_with_children"] = total_record_count
    
    return record_count, products


def extract_product_details(product, keep_selected_yes_or_no):
    product = dict(product)
    id = product.get("Product_ID")
    product_name = product.get("Product_Name")
    weight = product.get("Weight")
    magnitude = product.get("Magnitude")
    magnitude_unit = product.get("Magnitude_Unit")
    MRP = product.get("MRP")
    selling_price = product.get("Selling_Price")
    discount = product.get("Discount")
    brand_name = product.get("Brand")
    product.get("Stock_In_Hand")
    tlc_name = product.get("Main_Category")
    mlc_name = product.get("Sub_Category1")
    ilc_name = product.get("Sub_Category2")
    product_details = {
            "id" : id,
            "name" : product_name,
            "weight" : weight,
            "magnitude" : magnitude,
            "magnitude_unit" : magnitude_unit,
            "pricing" : {
                "mrp" : MRP,
                "selling_price" : selling_price,
                "discount" : discount
            },
            "brand" : {
                "name" : brand_name
            },
            "category" : {
                "tlc_name" : tlc_name,
                "mlc_name" : mlc_name,
                "ilc_name" : ilc_name
            },
            "keep_selected" : keep_selected_yes_or_no
        }
    
    return product_details


def reorder_based_on_user_weight_preference(top_matched_productID_product_details,
                                            user_request_product_weight_adjusted,
                                            user_request_product_weight_unit_adjusted
                                        ):

    # print("WITHIN reorder_based_on_user_weight_preference METHOD")
    # print("user_request_product_weight_adjusted:", user_request_product_weight_adjusted)
    # print("user_request_product_weight_unit_adjusted:", user_request_product_weight_unit_adjusted)
    
    matching_product_list= []
    non_matching_product_list= []
    top_matched_productID_product_details_reordered = []
    
    user_request_product_weight_adjusted = int(str(user_request_product_weight_adjusted).strip())
    user_request_product_weight_unit_adjusted = str(user_request_product_weight_unit_adjusted).strip().lower()
    # print("------------------------------------------------------------------------------")
    # print("user_request_product_weight_adjusted:", user_request_product_weight_adjusted)
    # print("user_request_product_weight_unit_adjusted:", user_request_product_weight_unit_adjusted)
    
    for product in top_matched_productID_product_details:
        product_weight = str(product.get("Weight")).strip().lower()
        product_magnitude = int(product.get("Magnitude"))
        product_magnitude_unit = str(product.get("Magnitude_Unit")).strip().lower()
        
        # print("product_magnitude:", product_magnitude)
        # print("product_magnitude_unit:", product_magnitude_unit)
        
        if (product_magnitude ==  user_request_product_weight_adjusted and 
            product_magnitude_unit == user_request_product_weight_unit_adjusted):  
            matching_product_list.append(product)
        else:
            non_matching_product_list.append(product)
    
    # Sort matching and non-matching lists by similarityScore in descending order
    matching_product_list.sort(key=lambda x: -x.get("similarityScore"))   
    non_matching_product_list.sort(key=lambda x: -x.get("similarityScore"))
                                                                
    # Combine the lists with matching products first
    top_matched_productID_product_details_reordered = matching_product_list + non_matching_product_list
    
    # just_for_display_purpose = [
    #     product.get('Product_ID')
    #     for product in top_matched_productID_product_details_reordered
    # ]
    # print("***************************************************************************************")
    # print("REORDERED PRODUCT IDS:", just_for_display_purpose)
    
    
    # just_for_display_purpose = [
    #     {"reorderedProductID" : product.get('Product_ID'), "similarityScore": product.get('similarityScore')}
    #     for product in top_matched_productID_product_details_reordered
    # ]
    # print("***************************************************************************************")
    # print("REORDERED PRODUCT IDS WITH SIMILARITY SCORES:", just_for_display_purpose)
    
    # for product in top_matched_productID_product_details_reordered:
    #     print(f"reordered product id: {product.get('Product_ID')}, similarity score: {product.get('similarityScore')}")
        
    return top_matched_productID_product_details_reordered


def find_top_matched_product_ids_with_multiple_similarities(
    user_request_product_embedding, product_embeddings_df, top_n
):

    print("find_top_matched_product_ids_with_multiple_similarities")

    pearson_correlation_list = []
    spearman_correlation_list = []
    kendall_correlation_list = []
    euclidean_distance_list = []
    manhattan_distance_list = []
    dot_product_list = []
    top_matched_product_ids_per_pearson_correlation = []
    top_matched_product_ids_per_spearman_correlation = []
    top_matched_product_ids_per_kendall_correlation = []
    top_matched_product_ids_per_euclidean_similarity = []
    top_matched_product_ids_per_manhattan_similarity = []
    top_matched_product_ids_per_dot_product = []

    user_request_product_embedding_array = np.array(
        user_request_product_embedding.tolist()
    ).reshape(1, -1)
    user_request_product_embedding_array_flattened = (
        user_request_product_embedding_array.flatten()
    )

    all_product_embeddings_array = np.array(
        product_embeddings_df["embedding"].tolist()
    ).reshape(len(product_embeddings_df), -1)

    for index, embedding in enumerate(all_product_embeddings_array):
        embedding_flattened = embedding.flatten()

        # Pearson Correlation
        pearson_value, pearson_pvalue = pearsonr(
            user_request_product_embedding_array_flattened, embedding_flattened
        )

        # Spearman Correlation
        spearman_value, spearman_pvalue = spearmanr(
            user_request_product_embedding_array_flattened, embedding_flattened
        )

        # Kendall Tau
        kendall_value, kendall_pvalue = kendalltau(
            user_request_product_embedding_array_flattened, embedding_flattened
        )

        # Euclidean Distance
        euclidean_distance = euclidean(
            user_request_product_embedding_array_flattened, embedding_flattened
        )
        euclidean_similarity = 1 / (1 + euclidean_distance)

        # Manhattan Distance
        manhattan_distance = cityblock(
            user_request_product_embedding_array_flattened, embedding_flattened
        )
        manhattan_similarity = 1 / (1 + manhattan_distance)

        # Dot Product
        dot_product = np.dot(
            user_request_product_embedding_array_flattened, embedding_flattened
        )

        pearson_correlation_list.append({"index": index, "correlation": pearson_value})
        spearman_correlation_list.append(
            {"index": index, "correlation": spearman_value}
        )
        kendall_correlation_list.append({"index": index, "correlation": kendall_value})
        euclidean_distance_list.append(
            {
                "index": index,
                "distance": euclidean_distance,
                "similarity": euclidean_similarity,
            }
        )
        manhattan_distance_list.append(
            {
                "index": index,
                "distance": manhattan_distance,
                "similarity": manhattan_similarity,
            }
        )
        dot_product_list.append({"index": index, "dot_product": dot_product})

    # Sorting and selecting top N results based on Pearson:
    pearson_correlation_sorted = sorted(
        pearson_correlation_list, key=lambda x: x["correlation"], reverse=True
    )
    top_matched_records = pearson_correlation_sorted[:top_n]

    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")
        top_matched_pearson_correlation_value = top_matched_record.get("correlation")
        top_matched_product_ids_per_pearson_correlation.append(
            {
                "productID": product_embeddings_df["productID"].iloc[top_matched_index],
                "correlation": top_matched_pearson_correlation_value,
            }
        )
    # Sorting and selecting top N results based on Spearman:
    spearman_correlation_sorted = sorted(
        spearman_correlation_list, key=lambda x: x["correlation"], reverse=True
    )
    top_matched_records = spearman_correlation_sorted[:top_n]

    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")
        top_matched_spearman_correlation_value = top_matched_record.get("correlation")
        top_matched_product_ids_per_spearman_correlation.append(
            {
                "productID": product_embeddings_df["productID"].iloc[top_matched_index],
                "correlation": top_matched_spearman_correlation_value,
            }
        )
    print(
        "top_matched_product_ids_per_spearman_correlation list:",
        top_matched_product_ids_per_spearman_correlation,
    )

    # Sorting and selecting top N results based on Kendall Tau:
    kendall_correlation_sorted = sorted(
        kendall_correlation_list, key=lambda x: x["correlation"], reverse=True
    )
    top_matched_records = kendall_correlation_sorted[:top_n]

    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")
        top_matched_kendall_correlation_value = top_matched_record.get("correlation")
        top_matched_product_ids_per_kendall_correlation.append(
            {
                "productID": product_embeddings_df["productID"].iloc[top_matched_index],
                "correlation": top_matched_kendall_correlation_value,
            }
        )
    print(
        "top_matched_product_ids_per_kendall_correlation list:",
        top_matched_product_ids_per_kendall_correlation,
    )

    # Sorting and selecting top N results based on Euclidean distance:
    euclidean_distance_list_sorted = sorted(
        euclidean_distance_list, key=lambda x: x["similarity"], reverse=True
    )
    top_matched_records = euclidean_distance_list_sorted[:top_n]

    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")
        top_matched_euclidean_similarity_value = top_matched_record.get("similarity")
        top_matched_product_ids_per_euclidean_similarity.append(
            {
                "productID": product_embeddings_df["productID"].iloc[top_matched_index],
                "similarity": top_matched_euclidean_similarity_value,
            }
        )
    print(
        "top_matched_product_ids_per_euclidean_similarity list:",
        top_matched_product_ids_per_euclidean_similarity,
    )

    # Sorting and selecting top N results based on Manhattan distance:
    manhattan_distance_list_sorted = sorted(
        manhattan_distance_list, key=lambda x: x["similarity"], reverse=True
    )
    top_matched_records = manhattan_distance_list_sorted[:top_n]

    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")
        top_matched_manhattan_similarity_value = top_matched_record.get("similarity")
        top_matched_product_ids_per_manhattan_similarity.append(
            {
                "productID": product_embeddings_df["productID"].iloc[top_matched_index],
                "similarity": top_matched_manhattan_similarity_value,
            }
        )
    print(
        "top_matched_product_ids_per_manhattan_similarity list:",
        top_matched_product_ids_per_manhattan_similarity,
    )

    # Sorting and selecting top N results based on Manhattan distance:
    dot_product_list_sorted = sorted(
        dot_product_list, key=lambda x: x["dot_product"], reverse=True
    )
    top_matched_records = dot_product_list_sorted[:top_n]

    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")
        top_matched_dot_product_value = top_matched_record.get("dot_product")
        top_matched_product_ids_per_dot_product.append(
            {
                "productID": product_embeddings_df["productID"].iloc[top_matched_index],
                "similarity": top_matched_dot_product_value,
            }
        )
    print(
        "top_matched_product_ids_per_dot_product list:",
        top_matched_product_ids_per_dot_product,
    )

    # return top_matched_products, spearman_correlation_list, kendall_correlation_list, euclidean_distance_list, manhattan_distance_list, dot_product_list


@app.route("/health", methods=["GET"])
def get_health():
    return "Ok"


@app.route("/orders/compose", methods=["GET"])
def compose_order():
    print("Within OrderManagementAPI.py compose order:", request.args)
    best_matched_productID_product_info = []
    all_product_details = []
    min_acceptable_cosine_similarity = 0.67
    total_record_processed_count = 0
    # 1. MODEL "multi-qa-mpnet-base-cos-v1"
    model_name_multi_qa_mpnet_base_cos = "multi-qa-mpnet-base-cos-v1"
    product_embeddings_file_path_multi_qa_mpnet_base_cos = (
        "product_embeddings_multi_qa_mpnet_base_cos_D250824.pkl"
    )

    # 2. MODEL "paraphrase-multilingual-mpnet-base-v2"
    model_name_paraphrase_multilingual_mpnet_base = (
        "paraphrase-multilingual-mpnet-base-v2"
    )
    product_embeddings_file_path_paraphrase_multilingual_mpnet_base = (
        "product_embeddings_paraphrase_multilingual_mpnet_D250824A.pkl"
    )

    # 3. MODEL "roberta-base-nli-stsb-mean-tokens", required for identifying the correct brand
    model_name_roberta_base_nli_stsb_mean_tokens = "roberta-base-nli-stsb-mean-tokens"
    brand_name_embeddings_file_path = "brand_name_embeddings.pkl"

    top_n = 20
    file_open_mode = "rb"

    # Open pickle files
    brand_name_embeddings_file_obj = open_pickle_files(
        brand_name_embeddings_file_path, file_open_mode
    )

    product_embeddings_file_obj_multi_qa_mpnet_base_cos = open_pickle_files(
        product_embeddings_file_path_multi_qa_mpnet_base_cos, file_open_mode
    )

    product_embeddings_file_obj_paraphrase_multilingual_mpnet_base = open_pickle_files(
        product_embeddings_file_path_paraphrase_multilingual_mpnet_base, file_open_mode
    )

    if (
        (product_embeddings_file_obj_multi_qa_mpnet_base_cos is None)
        or (product_embeddings_file_obj_paraphrase_multilingual_mpnet_base is None)
        or (brand_name_embeddings_file_obj is None)
    ):
        print("Failed to open the pickle file, exiting the program.")
        return "ERROR: Could Not Open Pickle Files."
    else:
        # Load the saved embeddings files into a dataframe
        brand_name_embeddings_df = load_embeddings(brand_name_embeddings_file_obj)
        product_embeddings_df_multi_qa_mpnet_base_cos = load_embeddings(
            product_embeddings_file_obj_multi_qa_mpnet_base_cos
        )
        product_embeddings_df_paraphrase_multilingual_mpnet_base = load_embeddings(
            product_embeddings_file_obj_paraphrase_multilingual_mpnet_base
        )

        # Close pickle files
        close_pickle_files(product_embeddings_file_obj_multi_qa_mpnet_base_cos)
        close_pickle_files(
            product_embeddings_file_obj_paraphrase_multilingual_mpnet_base
        )
        close_pickle_files(brand_name_embeddings_file_obj)

        # get the order details that the customer has requested.
        order_details = get_order_details_request()
        order_details_json = destructure_order_details(order_details)
        print("order_details_json:", order_details_json)
        
        # Load the SentenceTransformer models
        model_multi_qa_mpnet_base_cos = SentenceTransformer(
            model_name_multi_qa_mpnet_base_cos
        )
        model_paraphrase_multilingual_mpnet_base = SentenceTransformer(
            model_name_paraphrase_multilingual_mpnet_base
        )
        model_for_name_embeddings = SentenceTransformer(
            model_name_roberta_base_nli_stsb_mean_tokens
        )

        # Process for each product
        for product in order_details_json:
            print(
                "#################################################################################"
            )
            print("product:", product)
            user_request_product_name = str(product.get("item")).strip().lower()
            user_request_brand_name = str(product.get("brand")).strip().lower()
            user_request_product_weight = int(str(product.get("weight")).strip())
            user_request_product_weight_unit = (
                str(product.get("weightUnits")).strip().lower()
            )

            # Determine the best matched brand name as per user request
            best_matched_brand_name = process_user_request_brand(
                user_request_brand_name,
                model_for_name_embeddings,
                brand_name_embeddings_df,
            )

            print("best_matched_brand_name:", best_matched_brand_name)
            isFirst_Time = True

            # Process with MODEL "multi-qa-mpnet-base-cos-v1"
            top_matched_product_ids_with_similarity_scores = process_product(
                user_request_product_name,
                best_matched_brand_name,
                user_request_product_weight,
                user_request_product_weight_unit,
                model_multi_qa_mpnet_base_cos,
                product_embeddings_df_multi_qa_mpnet_base_cos,
                min_acceptable_cosine_similarity,
                isFirst_Time,
                top_n,
            )
            # Best matched product ID & similarity score
            best_matched_productID = top_matched_product_ids_with_similarity_scores[
                0
            ].get("productID")
            best_matched_productID_cosine_similarity = (
                top_matched_product_ids_with_similarity_scores[0].get("similarityScore")
            )
            print(
                f"best matched productID: {best_matched_productID}, similarity score: {best_matched_productID_cosine_similarity}"
            )

            # if the cosine similarty for the best matched product is not within acceptable range
            # do a recheck with
            if best_matched_productID_cosine_similarity:
                if (
                    best_matched_productID_cosine_similarity
                    < min_acceptable_cosine_similarity
                ):

                    isFirst_Time = False

                    # Process with MODEL "paraphrase-multilingual-mpnet-base-v2"
                    top_matched_product_ids_with_similarity_scores = process_product(
                        user_request_product_name,
                        best_matched_brand_name,
                        user_request_product_weight,
                        user_request_product_weight_unit,
                        model_paraphrase_multilingual_mpnet_base,
                        product_embeddings_df_paraphrase_multilingual_mpnet_base,
                        min_acceptable_cosine_similarity,
                        isFirst_Time,
                        top_n,
                    )

            top_matched_productID_product_details = [
                {**get_product_details(int(top_matched_product_id.get("productID"))), "similarityScore": top_matched_product_id.get("similarityScore")}  # type: ignore
                for top_matched_product_id in top_matched_product_ids_with_similarity_scores
            ]

            # print(
            #     "top_matched_product_ids_with_similarity_scores:",
            #     top_matched_product_ids_with_similarity_scores,
            # )

            ###### ADD WEIGHT FILTER #########
            
            user_request_product_weight_unit_standardized =  standardize_weight_units(user_request_product_weight_unit)
            
            match user_request_product_weight_unit_standardized:
                case "kg":
                    user_request_product_weight_adjusted = (user_request_product_weight * 1000)
                    user_request_product_weight_unit_adjusted = "g"
                
                case "l":
                    user_request_product_weight_adjusted = (user_request_product_weight * 1000)
                    user_request_product_weight_unit_adjusted = "ml"
                
                case default:
                    user_request_product_weight_adjusted = user_request_product_weight
                    user_request_product_weight_unit_adjusted = user_request_product_weight_unit_standardized    
            
            # print("BEFORE CALL")
            # print("user_request_product_weight_adjusted", user_request_product_weight_adjusted)
            # print("user_request_product_weight_unit_adjusted", user_request_product_weight_unit_adjusted)
            top_matched_productID_product_details_reordered = (
                reorder_based_on_user_weight_preference(top_matched_productID_product_details,
                                               user_request_product_weight_adjusted,
                                               user_request_product_weight_unit_adjusted
                                               )
            )

            record_count, best_matched_productID_product_info = prepare_API_response(top_matched_productID_product_details_reordered)
            all_product_details.append(best_matched_productID_product_info)
            total_record_processed_count += record_count
       
        print("total_record_processed_count:", total_record_processed_count)
        API_response = json.dumps(
            {
                "tabs": {
                    "product_info" : {
                        "products" : all_product_details
                        },
                    "total_count_of_all_products" : total_record_processed_count
                    }            
            }, 
            indent=4
        )
        # print("json_output:", json_output)   
            #convert into JSON API output format    
        return API_response
         # return best_matched_productID_product_info


@app.route("/orders/create", methods=["POST"])
def create_order():
    print("WITHIN CREATE ORDER. Received the order")

    def get_max_orderID_from_orders_collection(orders_collection):
        # sort the records in descending order based on orderID
        max_order = orders_collection.find_one(sort=[("orderID", -1)])
        max_orderID = int(max_order["orderID"])

        return max_orderID

    def insert_into_orders_collection(userConfirmedProducts, new_orderID):

        null_date = "0000-00-00T00:00:00.000Z"
        current_date=datetime.now()
        current_date_iso = current_date.isoformat()

        days_to_add = 7
        future_date=current_date + timedelta(days=days_to_add)
        future_date_iso = future_date.isoformat()

        inserted_result = orders_collection.insert_one(
        {
            "orderID": new_orderID,
            "userID": userConfirmedProducts.get("userID"),
            "items": userConfirmedProducts.get("products"),
            "orderConfirmedByUser": userConfirmedProducts.get("orderConfirmedByUser"),
            "orderCreatedDate": current_date_iso,
            "orderFulfilled": userConfirmedProducts.get("orderFulfilled"),
            "estimatedOrderFulfillmentDate": future_date_iso,
            "orderFulfillmentDate": null_date,
            "totalAmountMRP": userConfirmedProducts.get("totalAmountMRP"),
            "totalDiscountAmount": userConfirmedProducts.get("totalDiscountAmount"),
            "netTotalAmount": userConfirmedProducts.get("netTotalAmount"),
            "billingAddress": userConfirmedProducts.get("billingAddress"),
            "shippingAddress": userConfirmedProducts.get("shippingAddress"),
            "paymentMethod": userConfirmedProducts.get("paymentMethod"),
            "rowUpdateProcessID": "AndrewBotCreateOrders",
            "rowUpdateTimestamp": current_date_iso
        })

        return inserted_result

    data = request.get_json()
    if data:
        print("JSON Data:", json.dumps(data, indent=4))
        userConfirmedProducts = data.get("UserConfirmedProducts")

        max_orderID = get_max_orderID_from_orders_collection(orders_collection)

        new_orderID = max_orderID + 1

        inserted_result = insert_into_orders_collection(userConfirmedProducts, new_orderID)

        if inserted_result.acknowledged:
            print(
                f"New Order ID: {new_orderID} has been generated. Document inserted successfully. Inserted Document ID: {inserted_result.inserted_id}"
            )
            API_response = {"orderID" : new_orderID, "message" : "Order ID Successfully Generated"}
        else:
            print("Failed to insert document.")
            API_response = {"message" : "!!!ERROR: Document insertion failed!!!"}

    print("API_response:", API_response)
    
    return jsonify(API_response)


@app.route("/orders/view", methods=["GET"])
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
