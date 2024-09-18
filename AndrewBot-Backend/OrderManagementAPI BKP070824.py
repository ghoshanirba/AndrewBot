import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from pymongo import MongoClient
import sqlite3
import openai
import re
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

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


def match_order_with_products_inventory(item, brand, weight, weight_units):
    item = f"%{item}%"
    brand = f"%{brand}%"
    weight = weight
    weight_units = f"%{weight_units}%"
    
    #open database connection
    conn = sqlite3.connect(SQLITE_DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c1_cursor = conn.cursor()
    
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
                WHERE
                    LOWER(ProductName) LIKE LOWER(?)
                AND LOWER(Brand) LIKE LOWER(?)
                AND Weight = ?
                AND LOWER(WeightUnits LIKE LOWER(?)
                """

    
    result = c1_cursor.execute(SQL_QUERY, (item, brand, weight, weight_units))

    rows = result.fetchall()
    conn.close()
    
    # Check if any data is retrieved
    if not rows:
        print("No matching products found.")
        return None
    else:
        json_data_products = [dict(row) for row in rows]
        return json.dumps(json_data_products, indent=4)

# Function to convert order details from text to JSON format having 4 keys - item, brand, weight
# and weightUnits.
def destructure_order_details(order_details):
    order_details = order_details

    user_message = (
        f'Please parse the order - "{order_details}" and provide an output '
        'in JSON format having 4 keys - item, brand, weight and weightUnits. '
        'Default value of item, brand, weight and weightUnits is N.A. '
        'Assign default values whenever one of the key value pairs have not been obtained.'
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
                "passed.",
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
    print("Chat GPT Response:", chatGPT_response)

    try:
        # Parse the JSON response, the JSON output from chatGPT has a key "order"
        parsed_response = json.loads(chatGPT_response)

        # Extract the JSON content under the "order" key. If the key doesn't exist,
        # it returns an empty list [].
        order_details_json = parsed_response.get("order",[])
        return order_details_json

    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return []


def standardize_item_name(item_words):
    item_words = item_words
    item_text = ""
    standardized_words = []
    
    standardization_item_map = {
        "atta": "atta",
        "ata": "atta",
        "multigrain": "multigrains",
        "godihittu": "godihittu",
        "godihitu": "godihittu",
        "godhihittu": "godihittu",
        "godhihitu": "godihittu",
        "chakki": "chakki",
        "chaki": "chakki",
        "chakkki": "chakki",
        "sattu": "sattu",
        "chatu": "sattu",
        "ragi": "ragi",
        "raagi": "ragi",
        "raggi": "ragi",
        "raaggi": "ragi",
        "hittu": "hittu",
        "hitu": "hittu",
        "sooji": "sooji",
        "suji": "sooji",
        "sujji": "sooji",
        "soojji": "sooji",
        "shuji" : "sooji", 
        "shujji"  : "sooji",
        "shooji" : "sooji",
        "shoojji" : "sooji",
        "rava": "rava",
        "rawa": "rava",
        "chana": "chana",
        "channa": "chana",
        "chaana": "chana",
        "chaanna": "chana",
        "dal": "dal",
        "daal": "dal",
        "jowar": "jowar",
        "joar": "jowar",
    }

    for word in item_words:
        word = word.lower()
        #get standardized word if it exists in standardization_item_map, otherwise use the original word
        word_new = standardization_item_map.get(word, word)
        
        standardized_words.append(word_new)
        
    #join standardized words with a space    
    item_text = " ".join(standardized_words)
    
    return (item_text.lower())
    
def standardize_brand_name(brand_words):
    brand_words = brand_words
    brand_text = ""
    standardized_words = []
    
    standardization_brand_map = {
        "aashirvaad": "aashirvaad",
        "ashirvaad": "aashirvaad",
        "ashirvad": "aashirvaad",
        "aashirbaad": "aashirvaad",
        "ashirbaad": "aashirvaad",
        "ashirbad": "aashirvaad",
        "aashirwaad": "aashirvaad",
        "ashirwaad": "aashirvaad",
        "ashirwad": "aashirvaad",
        "manna": "manna",
        "mana": "manna",
        "weikfield": "weikfield",
        "wekfield": "weikfield",
        "sampann": "sampann",
        "sampan": "sampann",
        "weikfeld": "weikfield",
        "wekfeld": "weikfield",
    }

    for word in brand_words:
        word = word.lower()
        #get standardized word if it exists in standardization_brand_map, otherwise use the original word
        word_new = standardization_brand_map.get(word, word)
        
        standardized_words.append(word_new)
    
    #join standardized words with a space    
    brand_text = " ".join(standardized_words)
    
    return(brand_text.lower())


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

def get_wordnet_pos(word):
    word = word
    print("word:", word)
    
    #Map POS tag to first character lemmatize() accepts
    tag = nltk.pos_tag([word])[0][1][0].upper()
    
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV
    }

    #return wordnet.ADJ - a / wordnet.NOUN - n /wordnet.VERB - v /wordnet.ADV - r if 1st byte of 
    #nltk.pos_tag of a word is present in tag_dict. If not present return wordnet.NOUN - n as default.
    #This is done because nltk.pos_tag and lematize() from wordnet accepts POS differently.
    return tag_dict.get(tag, wordnet.NOUN)

def generate_tags(name):
    # Define stopwords to exclude
    custom_stopwords = set(stopwords.words('english') + ['with'] + ['made'])
    filtered_tokens = []
    
    # Normalize the text
    name = re.sub(r'\s+', ' ', name)  # Remove extra spaces
    name = re.sub(r'[^\w\s]', '', name)  # Remove special characters

    # Tokenize and lemmatize
    tokens = word_tokenize(name.lower())
    lemmatizer = WordNetLemmatizer()
    
    for token in tokens: 
        if token not in custom_stopwords:
            lematized_token = lemmatizer.lemmatize(token, get_wordnet_pos(token))
            filtered_tokens.append(lematized_token) #generates a list of lematized tokens.
        
    #Generate tag combinations
    tags = set()
    for i in range(len(filtered_tokens)):
        for j in range(i, len(filtered_tokens)):
            tag = '#' +''.join(filtered_tokens[i:j+1])
            if len(tag) > 1:  # Avoid single character tags
                tags.add(tag)

    return list(tags)


def get_product_ID_from_product_tags(item_name_tag_list, brand_name_tag_list):
    product_ID_list = []
    item_name_tag_list = item_name_tag_list
    brand_name_tag_list = brand_name_tag_list
    
    # Prepare the FTS query strings for items and brands
    item_name_tags_query = ' AND '.join(f'"{tag}"' for tag in item_name_tag_list)
    brand_name_tags_query = ' OR '.join(f'"{tag}"' for tag in brand_name_tag_list)
    
    print("item_name_tags_query:", item_name_tags_query)
    print("brand_name_tags_query:", brand_name_tags_query)
    
    SQL_QUERY = f"""
                    SELECT 
                        DISTINCT ProductID 
                    FROM 
                        ProductTagSearch
                    WHERE 
                        ProductTagName MATCH '{item_name_tags_query}'
                    AND BrandTagName MATCH '{brand_name_tags_query}'
                    """
    
    # # Prepare parameters for the query
    # params = item_name_tag_list + brand_name_tag_list
    # print("params:", params)   
    
    #open database connection
    conn = sqlite3.connect(SQLITE_DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c1_cursor = conn.cursor()
    
    print("SQL_QUERY:", SQL_QUERY)
    result = c1_cursor.execute(SQL_QUERY)

    rows = result.fetchall()
    conn.close()
    
    
    for row in rows:
        product_ID_list.append(row["ProductID"])
        
    
    # Check if any data is retrieved
    if not rows:
        print("No matching product ID found.")
        return None
    else:
        return list(product_ID_list)


@app.route("/health", methods=["GET"])
def get_health():
    return "Ok"


@app.route("/orders", methods=["POST"])
def create_order():
    print("Within OrderManagementAPI.py create order")

    data = request.json
    order_details = data.get("orderDetails", "").lower()
    
    # Regular expression to match any character that is not a letter, digit, comma, or space
    order_details_cleaned = re.sub(r'[^\w\s,]', '', order_details)
    print("order_details_cleaned:", order_details_cleaned)

    # order_details_json = destructure_order_details(order_details_cleaned)
    order_details_json = [
        {
            "item": "organic whole wheat",
            "brand": "ashirbaad",
            "weight": 5,
            "weightUnits": "kilo gram",
        },
        {
            "item": "chana chatu With Refreshing Drink Powder", 
            "brand": "mana", 
            "weight": 200, 
            "weightUnits": "grams"
        },
        {
            "item": "rice flour",
            "brand": "bb royal",
            "weight": 100,
            "weightUnits": "gram",
        }
    ]
    print("Parsed JSON:", json.dumps(order_details_json, indent=4))

    all_products_info = []
    for products in order_details_json:
        item = products.get("item")
        brand = products.get("brand")
        weight = products.get("weight")
        weight_units = products.get("weightUnits")

        print("Before standardization")
        print("======================")
        print("item:", item)
        print("brand:", brand)
        print("weight:", weight)
        print("weight_units:", weight_units)
        # split the item and brand names based on space for a product, a list will be returned since
        #split() method was used.
        item_words = item.split()
        brand_words = brand.split()

        print("item_words:", item_words)
        print("brand_words:", brand_words)

        # standardize item, brand and weight units for each product.
        standardized_item_name = standardize_item_name(item_words)
        standardized_brand_name = standardize_brand_name(brand_words)
        standardized_weight_units = standardize_weight_units(weight_units)
        
        print("After standardization")
        print("======================")
        print("standardized_item_name:", standardized_item_name)
        print("standardized_brand_name:", standardized_brand_name)
        print("un-standardized weight:", weight)
        print("standardized_weight_units:", standardized_weight_units)

        # generate tags for the standardized item and brand names.
        standardized_item_name_tags = generate_tags(standardized_item_name)
        print("standardized_item_name_tags:", standardized_item_name_tags)
        
        standardized_brand_name_tags = generate_tags(standardized_brand_name)
        print("standardized_brand_name_tags:", standardized_brand_name_tags)
        
        # do a look up in the ProductTags table for item and brand to find the product ID for
        # best matched tags.
        product_ID = get_product_ID_from_product_tags(standardized_item_name_tags, standardized_brand_name_tags)
        print("product_ID:", product_ID)
        # use the product ID to get the product details from Products table.
        #products_info_from_inventory = match_order_with_products_inventory(item, brand, weight, weight_units)
        

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
