# import json
# import requests
import gc
import re
import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# import os


def get_all_products_details():
    # Get all the details about products from Products SQLite table, database AndrewBotDB
    # SQLite connection details
    SQLITE_DATABASE_FILE = "./SQLiteDatabases/AndrewBotDB.db"
    SQL_QUERY = """
                SELECT 
                     Product_ID
                    ,Product_Name
                    ,USP
                    ,Weight
                    ,Brand
                    ,Main_Category
                    ,Sub_Category1
                    ,Sub_Category2
                    ,Product_Description
                FROM Products
                """
    # Column headers as defined in the SQL query
    column_headers = [
        "ProductID",
        "ProductName",
        "USP",
        "Weight",
        "Brand",
        "MainCategory",
        "SubCategory1",
        "SubCategory2",
        "ProductDescription",
    ]

    conn = sqlite3.connect(SQLITE_DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c1_cursor = conn.cursor()
    result = c1_cursor.execute(SQL_QUERY)

    rows = result.fetchall()
    df = pd.DataFrame(rows, columns=column_headers)
    conn.close()

    return df


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


def generate_input_text_for_name_embedding(
    productName_cleaned,
    mainCategory_cleaned,
    subCategory1_cleaned,
    subCategory2_cleaned,
):

    input_text = (
        f"The product is named {productName_cleaned}. It's main category is {mainCategory_cleaned}, "
        + f"1st sub-category is {subCategory1_cleaned} and 2nd sub-category is {subCategory2_cleaned}."
    )

    input_text = input_text.lower()

    return input_text


def generate_embedding(input_text, model):

    embedding = model.encode(input_text)

    return embedding


def open_pickle_files(file_path, file_open_mode):

    file_obj = open(file_path, file_open_mode)

    print(f"{file_path} pickle file opened.")

    return file_obj


def write_embeddings(embedding_list, file_object):

    try:
        embedding_df = pd.DataFrame(embedding_list)
        pickle.dump(embedding_df, file_object, protocol=pickle.HIGHEST_PROTOCOL)
        return f"Embedding have been saved"
    except pickle.PickleError as pe:
        return f"Failed to dump product embedding: {pe}"


def close_pickle_files(file_obj):
    file_obj.close()

    print("pickle files closed.")


def find_closest_product_ID(user_text_embedding, product_embedding_df):
    print("within find_closest_product_ID")
    user_text_embedding_array = np.array(user_text_embedding.tolist()).reshape(1, -1)
    embeddings = np.array(product_embedding_df["embedding"].tolist())

    print("user_text_embedding_array shape:", user_text_embedding_array.shape)
    print("embeddings shape:", embeddings.shape)

    similarities = cosine_similarity(user_text_embedding_array, embeddings)[0]
    best_matched_index = np.argmax(similarities)
    best_matched_product_id = product_embedding_df["productID"][best_matched_index]
    return best_matched_product_id


def process_unique_brands(
    unique_brandName, model, unique_brandName_embeddings_file_obj
):
    allowable_chars_brand = "&"
    replacement_char_brand = " "
    unique_brandName_embedding_list = []

    brandName_cleaned = clean_input_string(
        unique_brandName, allowable_chars_brand, replacement_char_brand
    )

    unique_brandName_embedding = generate_embedding(brandName_cleaned, model)

    unique_brandName_embedding_list.append(
        {"Brand": unique_brandName, "brandEmbedding": unique_brandName_embedding}
    )

    status = write_embeddings(
        unique_brandName_embedding_list, unique_brandName_embeddings_file_obj
    )

    del (
        brandName_cleaned,
        unique_brandName_embedding,
        unique_brandName_embedding_list,
    )
    gc.collect()

    return status


def process_products(row, model, product_embeddings_file_obj):
    allowable_chars_product_name = "&%/+,.()-\'+"
    replacement_char_product_name = " "
    allowable_chars_main_category = "&,"
    replacement_char_main_category = " "
    allowable_chars_sub_category1 = "&,"
    replacement_char_sub_category1 = " "
    allowable_chars_sub_category2 = "&,()+-"
    replacement_char_sub_category2 = " "
    product_embedding_list = []
    allowable_chars_brand = "&"
    replacement_char_brand = " "
    allowable_chars_USP = "&%.,/+-,()\'"
    replacement_char_USP = " "

    productID    = row["ProductID"]
    productName  = str(row["ProductName"]).strip()
    brand        = str(row["Brand"]).strip()
    weight       = str(row["Weight"]).strip().lower()
    mainCategory = str(row["MainCategory"]).strip()
    subCategory1 = str(row["SubCategory1"]).strip()
    subCategory2 = str(row["SubCategory2"]).strip()
    USP          = str(row["USP"]).strip()

    productName_cleaned = clean_input_string(
        productName, allowable_chars_product_name, replacement_char_product_name
    )
    
    mainCategory_cleaned = clean_input_string(
        mainCategory, allowable_chars_main_category, replacement_char_main_category
    )
    subCategory1_cleaned = clean_input_string(
        subCategory1, allowable_chars_sub_category1, replacement_char_sub_category1
    )
    subCategory2_cleaned = clean_input_string(
        subCategory2, allowable_chars_sub_category2, replacement_char_sub_category2
    )

    brandName_cleaned = clean_input_string(
        brand, allowable_chars_brand, replacement_char_brand
    )
    
    #Create embeddings for product name
    # input_text_product_name = (
    #     f"The product is named {productName_cleaned}. "
    #     f"{productName_cleaned} is known for its quality."
    # )
    
    # input_text_product_name = input_text_product_name.lower()
    # product_name_embedding = generate_embedding(input_text_product_name, model)
    
    # #Create embeddings for brand name
    # input_text_brand_name = (
    #     f"The brand of this product is {brandName_cleaned}. "
    #     f"{brandName_cleaned} is a trusted and popular brand."
    # )

    # input_text_brand_name = input_text_brand_name.lower()
    # brand_name_embedding = generate_embedding(input_text_brand_name, model)
    
    # #Store both product name embedding and brand name embedding in a list
    # product_embedding_list.append(
    #     {
    #         "productID": productID, 
    #         "productName_embedding": product_name_embedding,
    #         "brandName_embedding" : brand_name_embedding
    #     }
    # )
    # input_text_product = (
    #              f"Product name: {productName_cleaned}. "
    #              f"Brand: {brandName_cleaned}. "
    #              f"{productName_cleaned} is a popular product by {brandName_cleaned}. "
    #              f"It is a {mainCategory_cleaned} item having good properties of "
    #              f"{subCategory1_cleaned} and is a part of {subCategory2_cleaned}."
    #             )
    
    if USP is None or USP.strip() == "":
        input_text_product = (
            f"Product name: {productName_cleaned}. "
            f"Brand: {brandName_cleaned}. "
            f"The name of the product is '{productName_cleaned}'. "
            f"It belongs to the brand '{brandName_cleaned}'. "
            f"'{productName_cleaned}' is known for its high quality and is a popular product by '{brandName_cleaned}'. "
            f"It is a {mainCategory_cleaned} item having good properties of "
            f"{subCategory1_cleaned} and is a part of {subCategory2_cleaned}. "
            f"This product is categorized under {mainCategory_cleaned}, specifically in {subCategory1_cleaned}, "
            f"and is part of the broader {subCategory2_cleaned} category. "
        )
    else:
        USP_cleaned = clean_input_string(USP, allowable_chars_USP, replacement_char_USP)
        
        input_text_product = (
            f"Product name: {productName_cleaned}. "
            f"Brand: {brandName_cleaned}. "
            f"The name of the product is '{productName_cleaned}'. "
            f"It belongs to the brand '{brandName_cleaned}'. "
            f"'{productName_cleaned}' is known for its high quality and is a popular product by '{brandName_cleaned}'. "
            f"It is a {mainCategory_cleaned} item having good properties of "
            f"{subCategory1_cleaned} and is a part of {subCategory2_cleaned}. "
            f"This product is categorized under {mainCategory_cleaned}, specifically in {subCategory1_cleaned}, "
            f"and is part of the broader {subCategory2_cleaned} category. "
            f"The product {productName_cleaned} is {USP_cleaned} which is its USP."
        )
    
    product_embedding = generate_embedding(input_text_product, model)
    
    product_embedding_list.append(
        {
            "productID": productID, 
            "embedding": product_embedding
        }
    )
    status = write_embeddings(product_embedding_list, product_embeddings_file_obj)

    # print("product_embedding_list2", product_embedding_list)

    del (
        productName_cleaned,
        brandName_cleaned,
        input_text_product,
        product_embedding,
        product_embedding_list,
    )
    gc.collect()

    return status


def main():
    user_text = "Masala Tea"

    product_description_embedding_list = []
    rec_process_count = 0
    total_recs_processed_counter = 0
    total_uniqueBrands_processed_counter = 0
    total_uniqueBrands_write_counter = 0
    total_product_names_write_counter = 0
    total_product_embeddings_write_counter = 0
    # Define weights
    product_name_weight = 0.7
    brand_name_weight = 0.6
    category_weight = 0.1

    #1. MODEL "roberta-base-nli-stsb-mean-tokens"
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
    
    # 5. MODEL "all-roberta-large-v1"
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
    # product_embeddings_file_path = "product_embeddings_paraphrase_multilingual_mpnet.pkl"
    
    # 9 . MODEL "distiluse-base-multilingual-cased-v2"
    # model_name = "distiluse-base-multilingual-cased-v2"
    # product_embeddings_file_path = "product_embeddings_distiluse_multilingual_cased.pkl"
    
    # 10 . MODEL "multi-qa-mpnet-base-cos-v1"
    model_name = "multi-qa-mpnet-base-cos-v1"
    product_embeddings_file_path = "product_embeddings_multi_qa_mpnet_base_cos.pkl"
    
    file_open_mode = "ab"

    product_embeddings_file_obj = open_pickle_files(
        product_embeddings_file_path, file_open_mode
    )

    products_inventory_df = get_all_products_details()
    print("Record count obtained for processing:", len(products_inventory_df))
    
    # Load the SentenceTransformer models - 
    model = SentenceTransformer(model_name)
    print("Model used to generate embeddings:", model_name)
    
    # Extract unique brands and form a dataframe
    # unique_brands_df = products_inventory_df[["Brand"]].drop_duplicates()
    # print("Count of unique brands:", len(unique_brands_df))

    # # Create embeddings for each unique brands
    # for index, brand in unique_brands_df.iterrows():
    #     unique_brandName = str(brand["Brand"]).strip()
    #     print("Processing Brand:", unique_brandName)
    #     status = process_unique_brands(
    #         unique_brandName, model, unique_brandName_embeddings_file_obj
    #     )

    #     if status == "Embedding have been saved":
    #         total_uniqueBrands_write_counter += 1
    #     else:
    #         print("ERROR OCCURRED DURING WRITING BRAND EMBEDDING PICKLE FILE")
    #         print("ERROR Brand:", unique_brandName)
    #         print(status)

    #     total_uniqueBrands_processed_counter += 1

    # print("Total unique brands processed:", total_uniqueBrands_processed_counter)
    # print("Total unique brand embedding records written:", total_uniqueBrands_write_counter)

    # Create embeddings for each product names.
    for index, row in products_inventory_df.iterrows():
        productID = row["ProductID"]

        print("Processing product ID:", productID)

        status = process_products(row, model, product_embeddings_file_obj)

        # if status == "Embedding have been saved":
        #     total_product_names_write_counter += 1
        # else:
        #     print("ERROR OCCURRED DURING WRITING EMBEDDING PICKLE FILE")
        #     print("ERROR productID:", productID)
        #     print(status)

        # status = process_products(row, model, product_embeddings_file_obj)

        if status == "Embedding have been saved":
            total_product_embeddings_write_counter += 1
        else:
            print("ERROR OCCURRED DURING WRITING PRODUCT EMBEDDING PICKLE FILE")
            print("ERROR productID:", productID)
            print(status)

        total_recs_processed_counter += 1
        rec_process_count += 1

        if rec_process_count == 50:
            print("Count of records processed:", total_recs_processed_counter)
            rec_process_count = 0

    print("Total product IDs processed:", total_recs_processed_counter)
    # print("Total product name embedding records written:", total_product_names_write_counter)
    print(
        "Total product embedding records written:",
        total_product_embeddings_write_counter,
    )

    close_pickle_files(product_embeddings_file_obj)

    ######################################################################
    # with open("product_embeddings.pkl", "rb") as f1:
    #     product_embedding_df1 = pickle.load(f1)
    # # print("product_embedding_df:", product_embedding_df)
    # f1.close()

    # user_text_embedding = generate_embedding(user_text.lower())
    # # print("user_text_embedding shape from main:", user_text_embedding.shape)

    # best_matched_product_id = find_closest_product_ID(user_text_embedding, product_embedding_df1)
    # print("best_matched_product_id:", best_matched_product_id)


if __name__ == "__main__":
    main()
