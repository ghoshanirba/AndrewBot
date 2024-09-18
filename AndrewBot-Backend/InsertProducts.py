import re
import sqlite3
import pandas as pd
from datetime import datetime

# SQLite connection details
SQLITE_DATABASE_FILE = "./SQLiteDatabases/AndrewBotDB.db"

# Define the path to your Excel file and the SQLite database
excel_file_path = "E:/MBA in BI & AI/SEM 4/Final Project/AndrewBot-Backend/BigBasket Scraped Data/Beverages/product_details_Beverages - consolidated.xlsb"

df = pd.read_excel(excel_file_path, engine="pyxlsb", sheet_name="Sheet1")
print("Record count in excel file:", len(df))
print("df datatypes:", df.dtypes)
# Open database connection
conn = sqlite3.connect(SQLITE_DATABASE_FILE)
c1_cursor = conn.cursor()

# Insert query
SQL_QUERY = """
                INSERT INTO Products
                (
                     Product_ID
                    ,Product_Name
                    ,USP
                    ,Weight
                    ,Magnitude
                    ,Magnitude_Unit
                    ,MRP
                    ,Selling_Price
                    ,Base_Price
                    ,Base_Price_Unit
                    ,Subscription_Price
                    ,Discount
                    ,Brand
                    ,Stock_In_Hand
                    ,Main_Category
                    ,Sub_Category1
                    ,Sub_Category2
                    ,Product_Average_Rating
                    ,Product_Description
                    ,Row_Update_Process_ID
                    ,Row_Update_Timestamp
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                
                """
insert_Count = 0
stockInHand = 50
userID = "ghoshanirban"
currentTimestamp = datetime.now()
pattern = r"[^a-zA-Z0-9\s.,!?:;'\"()\-+/*[\]{}&_%\\]"

for index, row in df.iterrows():
    productID = row["product_id"]
    productName = str(row["product_desc"]).strip()
    USP = str(row["product_USP"]).strip()
    weight = str(row["product_weight"]).strip()
    magnitude = row["magnitude"]
    magnitudeUnit = str(row["unit"]).strip()
    MRP = row["MRP"]
    sellingPrice = row["selling_price"]
    basePrice = row["base_price"]
    basePriceUnit = str(row["base_unit"]).strip()
    subscriptionPrice = row["subscription_price"]
    discount = str(row["discount_text"]).strip()
    brand = str(row["brand"]).strip()
    mainCategory = str(row["main_category"]).strip()
    subCategory1 = str(row["sub_category1"]).strip()
    subCategory2 = str(row["sub_category2"]).strip()
    productAvgRating = row["avg_rating"]
    productDescription = str(row["about_the_product"]).strip()

    productDescription = re.sub(pattern, ' ', productDescription)
    
    c1_cursor.execute(
        SQL_QUERY,
        (
            productID,
            productName,
            USP,
            weight,
            magnitude,
            magnitudeUnit,
            MRP,
            sellingPrice,
            basePrice,
            basePriceUnit,
            subscriptionPrice,
            discount,
            brand,
            stockInHand,
            mainCategory,
            subCategory1,
            subCategory2,
            productAvgRating,
            productDescription,
            userID,
            currentTimestamp,
        ),
    )
    
    insert_Count += 1
    
conn.commit()
conn.close()
print("Records inserted:", insert_Count)