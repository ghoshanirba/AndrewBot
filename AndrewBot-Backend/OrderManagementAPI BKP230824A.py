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
            {
                "item": "whole wheat atta",
                "brand": "ashirbaad",
                "weight": "5",
                "weightUnits": "kg",
            },
            {"item": "wheat", "brand": "pilsbury", "weight": "5", "weightUnits": "kg"},
            {"item": "sattu", "brand": "mana", "weight": "200", "weightUnits": "grams"},
            {
                "item": "rice flour",
                "brand": "bb royal",
                "weight": "100",
                "weightUnits": "gms",
            },
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
            # {
            #     "item": "seed and nut mix",
            #     "brand": "true elements",
            #     "weight": "1",
            #     "weightUnits": "ltr",
            # },
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


def open_pickle_files(filename, file_open_mode):
    try:
        f1 = open(filename, file_open_mode)
        print(f"{filename} pickle files opened in {file_open_mode} mode.")
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


def process_product(
    user_request_product_name,
    best_matched_brand_name,
    user_request_product_weight,
    user_request_product_weight_unit,
    model,
    product_embeddings_df,
    top_n,
):
    allowable_chars_product_name = "&%"
    replacement_char_product_name = " "
    allowable_chars_category = "&"
    replacement_char_category = " "
    allowable_chars_brand_name = "&"
    replacement_char_brand_name = " "
    top_matched_product_ids = []
    product_name_weight = 0.5
    brand_name_weight = 0.5
    category_weight = 0.1
    best_matched_productID = None
    highest_similarity = -1
    cut_off_cosine_similarity = 0.67

    user_request_product_name_cleaned = clean_input_string(
        user_request_product_name,
        allowable_chars_product_name,
        replacement_char_product_name,
    )

    best_matched_brand_name_cleaned = clean_input_string(
        best_matched_brand_name, allowable_chars_brand_name, replacement_char_brand_name
    )

   
    # Create embeddings for user request product name, use this as main
    input_text_product = (
        f"What is the complete product name that contains {user_request_product_name_cleaned} "
        f"and having the brand name {best_matched_brand_name_cleaned}."
    )     

    print("input_text_product:", input_text_product)
    
    user_request_product_embedding = generate_embedding(input_text_product, model)

    ################### COSINE SIMILARITIES ####################
    # do a look up in the Products embedding file to find the best matched product ID.
    # best_matched_productID = find_closest_matched_product_ID(
    #     user_request_product_embedding, product_embeddings_df
    # )

    top_matched_product_ids, top_matched_product_ids_with_similarity_scores = (
        find_top_matched_product_ID(
            user_request_product_embedding, product_embeddings_df, top_n
        )
    )

    print("top_matched_product_ids_with_similarity_scores 1st element:",
          top_matched_product_ids_with_similarity_scores[0]
          )
    
    best_matched_productID = top_matched_product_ids_with_similarity_scores[0].get('productID')
    best_matched_productID_cosine_similarity = top_matched_product_ids_with_similarity_scores[0].get('similarityScore')
    
    if best_matched_productID_cosine_similarity is not None:
        if best_matched_productID_cosine_similarity < cut_off_cosine_similarity:
            # Create embeddings for user request product name, use this to do a recheck
            input_text_product = (
                f"Product name: {user_request_product_name_cleaned}. "
                f"Brand: {best_matched_brand_name_cleaned}. "
                f"{user_request_product_name_cleaned} is a popular product by {best_matched_brand_name_cleaned}. "
                f"This product is known for its quality and is widely recognized under the {best_matched_brand_name_cleaned} brand."
                )
            
            print("input_text_product:", input_text_product)
    
            user_request_product_embedding = generate_embedding(input_text_product, model)            
        
    ############################################################
    
    ################### PEARSON'S CORRELATION ##################
    # top_matched_product_ids_per_pearson_correlation = find_top_matched_product_ids_with_pearson_correlation(user_request_product_embedding, 
    #                                                           product_embeddings_df, top_n)
    
    # print("top_matched_product_ids_per_pearson_correlation:", top_matched_product_ids_per_pearson_correlation)
    ############################################################
    
    # find_top_matched_product_ids_with_multiple_similarities(user_request_product_embedding, 
    #                                                         product_embeddings_df, 
    #                                                         top_n)
    
    return (
        best_matched_productID,
        top_matched_product_ids,
        top_matched_product_ids_with_similarity_scores,
    )


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
    print("Maximum Cosine Similarity:", max_similarity)

    return best_matched_product_id


def find_top_matched_product_ID(
    user_request_product_embedding, product_embeddings_df, top_n
):
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
    top_indices = np.argsort(similarities)[::-1][:top_n]

    # Get the top N product IDs
    top_matched_product_ids = (
        product_embeddings_df["productID"].iloc[top_indices].tolist()
    )

    # Get the top N product IDs with their similarity scores
    top_matched_product_ids_with_similarity_scores = [
        {
            "productID": product_embeddings_df["productID"].iloc[index],
            "similarityScore": similarities[index],
        }
        for index in top_indices
    ]
    
    return top_matched_product_ids, top_matched_product_ids_with_similarity_scores


def find_top_matched_product_ids_with_pearson_correlation(user_request_product_embedding, 
                                                              product_embeddings_df, top_n):
    
    print("find_top_matched_product_ids_with_pearson_correlation")
    
    pearson_correlation_list = []
    top_matched_product_ids_per_pearson_correlation = []
    
    product_embeddings_df_len = len(product_embeddings_df)
    
    user_request_product_embedding_array = np.array(user_request_product_embedding.tolist()).reshape(1,-1)
    user_request_product_embedding_array_flattened = user_request_product_embedding_array.flatten()
    
    all_product_emdeddings_array = np.array(product_embeddings_df["embedding"].tolist()).reshape(product_embeddings_df_len,-1)
    
    # Calculate Pearson's correlation for each product embedding
    for index, embedding in enumerate(all_product_emdeddings_array):
        pearson_correlation_value, pearson_correlation_pvalue = pearsonr(user_request_product_embedding_array_flattened, embedding)
        pearson_correlation_list.append(
            {
                "index" : index, 
                "correlation" : pearson_correlation_value, 
                "pvalue":pearson_correlation_pvalue
            }
        )
    
    #Sort the pearson_correlation_list in descending order on pearson_correlation_value which is x[1]
    pearson_correlation_list_sorted = sorted(pearson_correlation_list, key=lambda x: x["correlation"], reverse=True)
    
    top_matched_records = pearson_correlation_list_sorted[:top_n]
    
    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")    
        top_matched_pearson_correlation_value = top_matched_record.get("correlation")
        top_matched_pearson_correlation_pvalue = top_matched_record.get("pvalue")
        top_matched_product_ids_per_pearson_correlation.append(
            {
                "productID" : product_embeddings_df["productID"].iloc[top_matched_index],
                "correlation" : top_matched_pearson_correlation_value,
                "pvalue" : top_matched_pearson_correlation_pvalue
            }          
        )
    
    return top_matched_product_ids_per_pearson_correlation



def find_top_matched_product_ids_with_multiple_similarities(user_request_product_embedding, 
                                                            product_embeddings_df, 
                                                            top_n):
    
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
    
    user_request_product_embedding_array = np.array(user_request_product_embedding.tolist()).reshape(1, -1)
    user_request_product_embedding_array_flattened = user_request_product_embedding_array.flatten()
    
    all_product_embeddings_array = np.array(product_embeddings_df["embedding"].tolist()).reshape(len(product_embeddings_df), -1)
    
    for index, embedding in enumerate(all_product_embeddings_array):
        embedding_flattened = embedding.flatten()
        
        # Pearson Correlation
        pearson_value, pearson_pvalue = pearsonr(user_request_product_embedding_array_flattened, embedding_flattened)
        
        # Spearman Correlation
        spearman_value, spearman_pvalue = spearmanr(user_request_product_embedding_array_flattened, embedding_flattened)
        
        # Kendall Tau
        kendall_value, kendall_pvalue = kendalltau(user_request_product_embedding_array_flattened, embedding_flattened)
        
        # Euclidean Distance
        euclidean_distance = euclidean(user_request_product_embedding_array_flattened, embedding_flattened)
        euclidean_similarity = 1 / (1 + euclidean_distance)
        
        # Manhattan Distance
        manhattan_distance = cityblock(user_request_product_embedding_array_flattened, embedding_flattened)
        manhattan_similarity = 1 / (1 + manhattan_distance)
        
        # Dot Product
        dot_product = np.dot(user_request_product_embedding_array_flattened, embedding_flattened)
        
        pearson_correlation_list.append({"index": index, "correlation": pearson_value})
        spearman_correlation_list.append({"index": index, "correlation": spearman_value})
        kendall_correlation_list.append({"index": index, "correlation": kendall_value})
        euclidean_distance_list.append({"index": index, "distance": euclidean_distance, "similarity": euclidean_similarity})
        manhattan_distance_list.append({"index": index, "distance": manhattan_distance, "similarity": manhattan_similarity})
        dot_product_list.append({"index": index, "dot_product": dot_product})
    
    # Sorting and selecting top N results based on Pearson:
    pearson_correlation_sorted = sorted(pearson_correlation_list, key=lambda x: x["correlation"], reverse=True)
    top_matched_records = pearson_correlation_sorted[:top_n]
    
    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")    
        top_matched_pearson_correlation_value = top_matched_record.get("correlation")
        top_matched_product_ids_per_pearson_correlation.append(
            {
                "productID" : product_embeddings_df["productID"].iloc[top_matched_index],
                "correlation" : top_matched_pearson_correlation_value
            }          
        )
    # Sorting and selecting top N results based on Spearman:
    spearman_correlation_sorted = sorted(spearman_correlation_list, key=lambda x: x["correlation"], reverse=True)
    top_matched_records = spearman_correlation_sorted[:top_n]
    
    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")    
        top_matched_spearman_correlation_value = top_matched_record.get("correlation")
        top_matched_product_ids_per_spearman_correlation.append(
            {
                "productID" : product_embeddings_df["productID"].iloc[top_matched_index],
                "correlation" : top_matched_spearman_correlation_value
            }          
        )
    print("top_matched_product_ids_per_spearman_correlation list:", top_matched_product_ids_per_spearman_correlation)
    
    # Sorting and selecting top N results based on Kendall Tau:
    kendall_correlation_sorted = sorted(kendall_correlation_list, key=lambda x: x["correlation"], reverse=True)
    top_matched_records = kendall_correlation_sorted[:top_n]
    
    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")    
        top_matched_kendall_correlation_value = top_matched_record.get("correlation")
        top_matched_product_ids_per_kendall_correlation.append(
            {
                "productID" : product_embeddings_df["productID"].iloc[top_matched_index],
                "correlation" : top_matched_kendall_correlation_value
            }          
        )
    print("top_matched_product_ids_per_kendall_correlation list:", top_matched_product_ids_per_kendall_correlation)
    
    # Sorting and selecting top N results based on Euclidean distance:
    euclidean_distance_list_sorted = sorted(euclidean_distance_list, key=lambda x: x["similarity"], reverse=True)
    top_matched_records = euclidean_distance_list_sorted[:top_n]
    
    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")    
        top_matched_euclidean_similarity_value = top_matched_record.get("similarity")
        top_matched_product_ids_per_euclidean_similarity.append(
            {
                "productID" : product_embeddings_df["productID"].iloc[top_matched_index],
                "similarity" : top_matched_euclidean_similarity_value
            }          
        )
    print("top_matched_product_ids_per_euclidean_similarity list:", top_matched_product_ids_per_euclidean_similarity)
    
    # Sorting and selecting top N results based on Manhattan distance:
    manhattan_distance_list_sorted = sorted(manhattan_distance_list, key=lambda x: x["similarity"], reverse=True)
    top_matched_records = manhattan_distance_list_sorted[:top_n]
    
    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")    
        top_matched_manhattan_similarity_value = top_matched_record.get("similarity")
        top_matched_product_ids_per_manhattan_similarity.append(
            {
                "productID" : product_embeddings_df["productID"].iloc[top_matched_index],
                "similarity" : top_matched_manhattan_similarity_value
            }          
        )
    print("top_matched_product_ids_per_manhattan_similarity list:", top_matched_product_ids_per_manhattan_similarity)
    
    # Sorting and selecting top N results based on Manhattan distance:
    dot_product_list_sorted = sorted(dot_product_list, key=lambda x: x["dot_product"], reverse=True)
    top_matched_records = dot_product_list_sorted[:top_n]
    
    for top_matched_record in top_matched_records:
        top_matched_index = top_matched_record.get("index")    
        top_matched_dot_product_value = top_matched_record.get("dot_product")
        top_matched_product_ids_per_dot_product.append(
            {
                "productID" : product_embeddings_df["productID"].iloc[top_matched_index],
                "similarity" : top_matched_dot_product_value
            }          
        )
    print("top_matched_product_ids_per_dot_product list:", top_matched_product_ids_per_dot_product)
    
    # return top_matched_products, spearman_correlation_list, kendall_correlation_list, euclidean_distance_list, manhattan_distance_list, dot_product_list


@app.route("/health", methods=["GET"])
def get_health():
    return "Ok"


@app.route("/orders", methods=["POST"])
def create_order():
    print("Within OrderManagementAPI.py create order")
    all_products_info = []
    best_matched_productID_product_info = []
    brand_name_embeddings_file_path = "brand_name_embeddings.pkl"
    # 1. MODEL "roberta-base-nli-stsb-mean-tokens"
    # model_name = "roberta-base-nli-stsb-mean-tokens"
    # product_embeddings_file_path = "product_embeddings_roberta.pkl"

    # 2. MODEL "distilbert-base-nli-stsb-mean-tokens"
    # model_name = "distilbert-base-nli-stsb-mean-tokens"
    # product_embeddings_file_path = "product_embeddings_distilbert.pkl"

    # 3. MODEL "all-MiniLM-L6-v2"
    # model_name = "all-MiniLM-L6-v2"
    # product_embeddings_file_path = "product_embeddings_minilm_l6.pkl"

    # 4. MODEL "paraphrase-MiniLM-L6-v2"
    # model_name = "paraphrase-MiniLM-L6-v2"
    # product_embeddings_file_path = "product_embeddings_paraphrase_MiniLM.pkl"

    # # 5. MODEL "all-roberta-large-v1"
    # model_name = "all-roberta-large-v1"
    # product_embeddings_file_path = "product_embeddings_roberta_large.pkl"

    # 6. MODEL "all-MPNet-base-v2"
    # model_name = "all-MPNet-base-v2"
    # product_embeddings_file_path = "product_embeddings_MPNet_base.pkl"

    # 7. MODEL "paraphrase-multilingual-MiniLM-L12-v2"
    # model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    # product_embeddings_file_path = "product_embeddings_paraphrase_multilingual_MiniLM.pkl"

    # 8. MODEL "paraphrase-multilingual-mpnet-base-v2"
    # model_name = "paraphrase-multilingual-mpnet-base-v2"
    # product_embeddings_file_path = (
    #     "product_embeddings_paraphrase_multilingual_mpnet_D220824A.pkl"
    # )

    # 9 . MODEL "distiluse-base-multilingual-cased-v2"
    # model_name = "distiluse-base-multilingual-cased-v2"
    # product_embeddings_file_path = "product_embeddings_distiluse_multilingual_cased.pkl"

    #  # 10 . MODEL "multi-qa-mpnet-base-cos-v1"
    model_name = "multi-qa-mpnet-base-cos-v1"
    product_embeddings_file_path = (
        "product_embeddings_multi_qa_mpnet_base_cos_D220824.pkl"
    )

    top_n = 20
    file_open_mode = "rb"

    # Open pickle files
    brand_name_embeddings_file_obj = open_pickle_files(
        brand_name_embeddings_file_path, file_open_mode
    )
    product_embeddings_file_obj = open_pickle_files(
        product_embeddings_file_path, file_open_mode
    )

    if (product_embeddings_file_obj is None) or (
        brand_name_embeddings_file_obj is None
    ):
        print("Failed to open the pickle file, exiting the program.")
        return "ERROR: Could Not Open Pickle Files."
    else:
        # Load the saved embeddings files into a dataframe
        brand_name_embeddings_df = load_embeddings(brand_name_embeddings_file_obj)
        product_embeddings_df = load_embeddings(product_embeddings_file_obj)

        # Close pickle files
        close_pickle_files(product_embeddings_file_obj)
        close_pickle_files(brand_name_embeddings_file_obj)

        # get the order details that the customer has requested.
        order_details = get_order_details_request()
        order_details_json = destructure_order_details(order_details)

        # Load the SentenceTransformer model
        model = SentenceTransformer(model_name)
        model_for_name_embeddings = SentenceTransformer(
            "roberta-base-nli-stsb-mean-tokens"
        )
        print("Model used to generate embeddings:", model_name)

        # Process for each product
        for product in order_details_json:
            print(
                "#################################################################################"
            )
            print("product:", product)
            user_request_product_name = str(product.get("item")).strip().lower()
            user_request_brand_name = str(product.get("brand")).strip().lower()
            user_request_product_weight = str(product.get("weight")).strip().lower()
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

            # Find best matched product ID
            (
                best_matched_productID,
                top_matched_product_ids,
                top_matched_product_ids_with_similarity_scores,
            ) = process_product(
                user_request_product_name,
                best_matched_brand_name,
                user_request_product_weight,
                user_request_product_weight_unit,
                model,
                product_embeddings_df,
                top_n,
            )

            print("best matched productID:", best_matched_productID)

            # use the product ID to get the product details from Products table.
            if best_matched_productID:
                best_matched_productID_product_details = get_product_details(
                    int(best_matched_productID)
                )
                print(
                    "best_matched_productID_product_details:",
                    best_matched_productID_product_details,
                )

                if best_matched_productID_product_details:
                    best_matched_productID_product_info.append(
                        best_matched_productID_product_details
                    )

            print("top_matched_product_ids:", top_matched_product_ids)
            print(
                "top_matched_product_ids_with_similarity_scores:",
                top_matched_product_ids_with_similarity_scores,
            )

            ################################################################
            # Check if the user requested organic products
            user_requested_organic = "organic" in user_request_product_name

            # Fetch and filter product details
            # top_matched_productID_product_info = [
            #     top_matched_productID_product_details
            #     for top_matched_product_id in top_matched_product_ids
            #     if (top_matched_productID_product_details := get_product_details(int(top_matched_product_id))) is not None
            #     if (top_matched_product_product_name := top_matched_productID_product_details.get("Product_Name", "").lower())
            #     if (top_matched_product_sub_category1 := top_matched_productID_product_details.get("Sub_Category1", "").lower())
            #     if (top_matched_product_sub_category2 := top_matched_productID_product_details.get("Sub_Category2", "").lower())
            #     if (is_organic_product := (
            #         "organic" in top_matched_product_product_name or
            #         "organic" in top_matched_product_sub_category1 or
            #         "organic" in top_matched_product_sub_category2
            #     ))
            #     if (user_requested_organic and is_organic_product) or (not user_requested_organic and not is_organic_product)
            # ]

            # top_matched_productID_product_info = [
            #     top_matched_productID_product_details
            #     for top_matched_product_id in top_matched_product_ids
            #     if (top_matched_productID_product_details := get_product_details(int(top_matched_product_id))) is not None
            # ]

            #################################################################

            # Check if the user requested organic products
            # user_requested_organic = "organic" in user_request_product_name
            top_matched_productID_product_info = []

            # for top_matched_product_id in top_matched_product_ids:
            #     top_matched_productID_product_details = get_product_details(
            #         int(top_matched_product_id)
            #     )
            #     if top_matched_productID_product_details is not None:
            #         top_matched_product_product_name = (
            #             top_matched_productID_product_details.get(
            #                 "Product_Name", ""
            #             ).lower()
            #         )
            #         top_matched_product_sub_category1 = (
            #             top_matched_productID_product_details.get(
            #                 "Sub_Category1", ""
            #             ).lower()
            #         )
            #         top_matched_product_sub_category2 = (
            #             top_matched_productID_product_details.get(
            #                 "Sub_Category2", ""
            #             ).lower()
            #         )

            #         # Determine if the product is organic
            #         is_organic_product = (
            #             "organic" in top_matched_product_product_name
            #             or "organic" in top_matched_product_sub_category1
            #             or "organic" in top_matched_product_sub_category2
            #         )
            #         # Remove organic items if the user has not requested for it explicitely
            #         if user_requested_organic:
            #             if is_organic_product:
            #                 # include only organic products
            #                 top_matched_productID_product_info.append(
            #                     top_matched_productID_product_details
            #                 )
            #         else:
            #             if not is_organic_product:
            #                 # include only inorganic products
            #                 top_matched_productID_product_info.append(
            #                     top_matched_productID_product_details
            #                 )

            # for row in top_matched_productID_product_info:
            #     print("top_matched_productID_product_info:", row)
            #     print("*****************************************")

    return best_matched_productID_product_info


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
