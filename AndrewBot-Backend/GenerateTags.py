from datetime import datetime
from pymongo import MongoClient
import sqlite3
import re
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')


# MongoDB Atlas connection details
MONGO_URI = "mongodb+srv://ghoshanirba:Xy1EGbmjh3oYJC2r@cluster0.y5lid8k.mongodb.net/"
DATABASE_NAME = "AndrewBot"
COLLECTION_NAME = "ProductTags"

# SQLite connection details
SQLITE_DATABASE_FILE = "./SQLiteDatabases/AndrewBotDB.db"

# Initialize MongoDB Client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
product_tags_collection = db[COLLECTION_NAME]


def get_products_inventory():
    
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
                    Brand
                FROM Products
                """

    
    result = c1_cursor.execute(SQL_QUERY)

    rows = result.fetchall()
    
    conn.close()
    products_inventory = []
    for row in rows:
        products_inventory.append(dict(row))
    # Check if any data is retrieved
    return products_inventory


def get_wordnet_pos(word):
    print("word:", word)
    """Map POS tag to first character lemmatize() accepts"""

    nltk_pos_tag = nltk.pos_tag([word])[0][1]
    print("nltk_pos_tag:", nltk_pos_tag)

    if nltk_pos_tag.startswith("N"):
      return wordnet.NOUN
    elif nltk_pos_tag.startswith("J"):
      return wordnet.ADJ
    else:
      return None

def generate_tags(description):
    # Define stopwords to exclude
    custom_stopwords = set(stopwords.words('english') + ['with'] + ['made'])
    
    # Normalize the text
    description = re.sub(r'\s+', ' ', description)  # Remove extra spaces
    description = re.sub(r'[^\w\s]', '', description)  # Remove special characters

    # Tokenize and lemmatize
    word_tokens = word_tokenize(description.lower())
    
    # Remove stopwords from word_tokens
    filtered_word_tokens = [token for token in word_tokens if token not in custom_stopwords]
    print("filtered_word_tokens:", filtered_word_tokens)
    
    #print("tokens:", tokens)
    lemmatizer = WordNetLemmatizer()
    
    # Get POS tags for bigrams to improve context
    bigram_tokens = list(nltk.bigrams(filtered_word_tokens))
    print("bigram_tokens:", bigram_tokens)
    
    bigram_tokens_formatted = []
    for bigram in bigram_tokens:
        print("bigram:", bigram)
        bigram_tokens_formatted_temp = '_'.join(bigram)
        bigram_tokens_formatted.append(bigram_tokens_formatted_temp)
    
    print("bigram_tokens_formatted:", bigram_tokens_formatted)

    tokens = filtered_word_tokens + bigram_tokens_formatted
    print("combined tokens:", tokens)
    
    filtered_tokens = []
    for token in tokens:
        wordnet_pos = get_wordnet_pos(token)
        
        if wordnet_pos in {wordnet.NOUN, wordnet.ADJ}:
            lematized_token = lemmatizer.lemmatize(token, wordnet_pos)
            filtered_tokens.append((lematized_token, wordnet_pos))
    
    #print("filtered_tokens:", filtered_tokens)
    
    tags = []
    hold_adjectives = ""

    for token, pos in filtered_tokens:
      
      if pos == wordnet.NOUN:
          if hold_adjectives:
              tags.append(f'{hold_adjectives}_{token}')
              hold_adjectives = ""
          else:
              tags.append(token)
      elif pos == wordnet.ADJ:
          if hold_adjectives:
              hold_adjectives = f'{hold_adjectives}_{token}'
          else:
              hold_adjectives = token
          tags.append(token)

    return tags


def add_tags_to_set(attribute, tags_set):
    """Generate tags for a given attribute and add them to the provided set."""
    tags = generate_tags(attribute)
    print("tags:", tags)
    tags_set.update(tags)

# Example usage
products_inventory = get_products_inventory()

for product in products_inventory:
    product_name_tags = set()
    print("product:", product)
    productID = product['ProductID']
    
    # Add tags for each product attribute
    add_tags_to_set(product['MainCategory'], product_name_tags)
    add_tags_to_set(product['SubCategory1'], product_name_tags)
    add_tags_to_set(product['SubCategory2'], product_name_tags)
    add_tags_to_set(product['ProductName'], product_name_tags)
    
    brand = product['Brand']
    
    print("productID:", productID)
    print("product_name_tags:", product_name_tags)
    print("product_brand:", brand)
    
    # Prepare the document to insert
    document = {
        "ProductID": productID,
        "ProductTagName": list(product_name_tags),
        "BrandTagName": brand,
        "RowUpdateProcessID": "ghoshanirban",
        "RowUpdateTimestamp": datetime.now()
    }
    
    # Insert the document into MongoDB
    product_tags_collection.insert_one(document)
    print(f"Inserted document for ProductID {product['ProductID']}")
    
    