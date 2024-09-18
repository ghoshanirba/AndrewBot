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


def clean_input_string(input_string):
    print("WITHIN clean_input_string")
    print("input_string:", input_string)
    # Replace '/' with a space
    input_string = str(input_string).strip().replace("/", " ")

    # Remove all characters except letters, digits, spaces, '&', and '%'
    cleaned_string = re.sub(r"[^a-zA-Z0-9&%\s]", "", input_string)

    return cleaned_string.strip()


def generate_input_text_for_embedding(
    productName_cleaned,
    brandName_cleaned,
    mainCategory_cleaned,
    subCategory1_cleaned,
    subCategory2_cleaned,
):

    input_text = (
        f"The product is named {productName_cleaned} and is from the brand {brandName_cleaned}. "
      + f"It belongs to the main category {mainCategory_cleaned}, 1st sub-category {subCategory1_cleaned} "
      + f"and 2nd sub-category {subCategory2_cleaned}."
    )

    input_text = input_text.lower()

    return input_text


def generate_embedding(input_text, model):

    embedding = model.encode(input_text)

    return embedding


def open_pickle_files():
    product_embeddings_file_path = "product_embeddings.pkl"
    product_description_embeddings_file_path = "product_description_embeddings.pkl"

    product_embeddings_file_obj = open(product_embeddings_file_path, "ab")

    product_description_embeddings_file_obj = open(
        product_description_embeddings_file_path, "ab"
    )
    print("pickle files opened.")

    return product_embeddings_file_obj, product_description_embeddings_file_obj


def write_embeddings(productID, embedding, flag, file_object):
    product_embedding_flag = "P"
    product_description_embedding_flag = "D"
    product_embedding_list = []
    product_description_embedding_list = []

    if flag == product_embedding_flag:
        try:
            product_embedding_list.append(
                {"productID": productID, "embedding": embedding}
            )
            product_embedding_df = pd.DataFrame(product_embedding_list)
            pickle.dump(
                product_embedding_df, file_object, protocol=pickle.HIGHEST_PROTOCOL
            )
            print(f"Product ID {productID} embedding have been saved.")
        except pickle.PickleError as pe:
            print(f"Failed to dump product embedding for product ID {productID}: {pe}")

    if flag == product_description_embedding_flag:
        try:
            product_description_embedding_list.append(
                {"productID": productID, "descriptionEmbedding": embedding}
            )
            product_description_embedding_df = pd.DataFrame(
                product_description_embedding_list
            )
            pickle.dump(
                product_description_embedding_df,
                file_object,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
            print(f"Product ID {productID} description embedding have been saved.")
        except pickle.PickleError as pe:
            print(
                f"Failed to dump product description embedding for product ID {productID}: {pe}"
            )

    del product_embedding_list, product_description_embedding_list
    gc.collect()


def close_pickle_files(
    product_embeddings_file_obj, product_description_embeddings_file_obj
):
    product_embeddings_file_obj.close()
    product_description_embeddings_file_obj.close()
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


def main():
    user_text = "Masala Tea"
    product_embedding_list = []
    product_description_embedding_list = []
    product_embedding_flag = "P"
    product_description_embedding_flag = "D"
    rec_process_count = 0
    total_recs_processed_counter = 0

    product_embeddings_file_obj, product_description_embeddings_file_obj = (
        open_pickle_files()
    )

    products_inventory_df = get_all_products_details()
    print("record count obtained for processing:", len(products_inventory_df))

    # Load the SentenceTransformer model RoBERTa
    model = SentenceTransformer("roberta-base-nli-stsb-mean-tokens")

    for index, row in products_inventory_df.iterrows():
        productID = row["ProductID"]
        productName = row["ProductName"]
        weight = row["Weight"]
        brand = row["Brand"]
        mainCategory = row["MainCategory"]
        subCategory1 = row["SubCategory1"]
        subCategory2 = row["SubCategory2"]
        productDescription = row["ProductDescription"]

        print("Processing product ID:", productID)

        productName_cleaned  = clean_input_string(productName)
        brandName_cleaned    = clean_input_string(brand)
        mainCategory_cleaned = clean_input_string(mainCategory)
        subCategory1_cleaned = clean_input_string(subCategory1)
        subCategory2_cleaned = clean_input_string(subCategory2)

        input_text = generate_input_text_for_embedding(
            productName_cleaned,
            brandName_cleaned,
            mainCategory_cleaned,
            subCategory1_cleaned,
            subCategory2_cleaned,
        )
        
        print("input_text:",  input_text)
        product_embedding = generate_embedding(input_text, model)

        write_embeddings(
            productID,
            product_embedding,
            product_embedding_flag,
            product_embeddings_file_obj,
        )

        # productDescription = str(productDescription).lower()
        # product_description_embedding = generate_embedding(productDescription, model)

        # write_embeddings(
        #     productID,
        #     product_description_embedding,
        #     product_description_embedding_flag,
        #     product_description_embeddings_file_obj,
        # )

        total_recs_processed_counter += 1
        rec_process_count += 1

        if rec_process_count == 50:
            print("Count of records processed:", total_recs_processed_counter)
            rec_process_count = 0

        del (
            input_text,
            product_embedding,
            productDescription,
            # product_description_embedding,
        )
        gc.collect()

    close_pickle_files(
        product_embeddings_file_obj, product_description_embeddings_file_obj
    )
    print("Total records processed:", total_recs_processed_counter)
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
