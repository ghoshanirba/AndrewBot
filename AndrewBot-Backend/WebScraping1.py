import requests
import json
import time

# URL to scrape
base_url = 'https://www.bigbasket.com/listing-svc/v2/products?type=pc&slug=fruits-vegetables'
delay_time = 5  # Adjust the delay time as needed (in seconds)
page_number = 1
data = []
all_product_details = []

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.bigbasket.com',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie' : 'x-entry-context-id=100; x-entry-context=bb-b2c; _bb_locSrc=default; x-channel=web; _bb_loid=j:null; _bb_bhid=; _bb_nhid=1723; _bb_vid=MTI3MTYyMjAwNjE=; _bb_dsevid=; _bb_dsid=; csrftoken=8oxjDnGDIhO9WMm3I8GyzVlj8as0SPmwTHtIqqr2LZlE6Ch5WnS3ExUFUltJGS69; _bb_home_cache=dd66856c.1.visitor; bb2_enabled=true; ufi=1; bigbasket.com=0591c50b-5f4f-4650-8ac4-fba1f789fbe3; _gcl_au=1.1.1389406266.1720768559; jarvis-id=82654d75-d81f-4b8e-b147-77eaef4e66b5; _bb_tc=0; _bb_rdt="MzEwNDYxMDgwMw==.0"; _bb_rd=6; adb=0; _gid=GA1.2.1009321565.1723119188; _client_version=2789; _bb_lat_long=MTIuOTQ5MTU4OTA3MXw3Ny41NzQwMjI2NzMx; _bb_hid=7427; BBAUTHTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjaGFmZiI6IjZfcTlIUHhkS3pra2xnIiwidGltZSI6MTcyMzE3OTc0NS4xMTY5NTkzLCJtaWQiOjYwMjY2NTA0LCJ2aWQiOjk5MDE4Mzg5NjMsImRldmljZV9pZCI6IldFQiIsInNvdXJjZV9pZCI6MSwiZWNfbGlzdCI6WzMsNCwxMCwxMiwxMywxNCwxNSwxNiwxNywyMCwxMDBdLCJURExUT0tFTiI6ImJjN2MyZjNkLThiMWItNDBmMy1hY2VmLWQwZTQxODFmZjM5ZCIsInJlZnJlc2hfdG9rZW4iOiI1OWNmYTgwYi0wZTc5LTRmMmItOTdiZS0zODA4ZTBjMjQxYTQiLCJ0ZGxfZXhwaXJ5IjoxNzIzNzg0NTQ0LCJleHAiOjE3Mzg5NTk3NDUsImlzX3NhZSI6bnVsbCwiZGV2aWNlX21vZGVsIjoiV0VCIiwiZGV2aWNlX2lzX2RlYnVnIjoiZmFsc2UifQ.4VTofu9_B9xKlDpGwHSpOtnhTEYqF1zi64j0YBWucyY; _bb_mid="MzA5Mjc0NzQ5NA=="; sessionid=4k6fwk0n9u845sc95yomlrltxu51yx1w; access_token=bc7c2f3d-8b1b-40f3-acef-d0e4181ff39d; _bb_bb2.0=1; is_global=0; _bb_addressinfo=; _bb_pin_code=; _bb_sa_ids=10179; _is_bb1.0_supported=0; _bb_cda_sa_info=djIuY2RhX3NhLjEwMC4xMDE3OQ==; is_integrated_sa=0; _bb_visaddr=; _gcl_gs=2.1.k1$i1723182717; _gac_UA-27455376-1=1.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _gcl_aw=GCL.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _bb_cid=1; _is_tobacco_enabled=0; ts="2024-08-09 16:38:33.264"; _bb_aid="Mjg3MTIxMjQ3NQ=="; _ga=GA1.2.1996715233.1720768560; _ga_FRRYG5VKHX=GS1.1.1723204010.10.0.1723204010.60.0.0; csurftoken=khWqJg.MTI3MTYyMjAwNjE=.1723207471433.jgxlJ+ulVL1cueaYs6DnByFwRApC1M/GWXzV4ZUNZiw='
}


try:
    # Make the GET request
    url = f'{base_url}&page={page_number}'
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        json_data = json.loads(response.text)
        # print(json.dumps(json_data, indent=4))
        print("Data retrieved successfully for page:", page_number)
    else:
        print(f"Error: Received status code {response.status_code}")

except requests.exceptions.RequestException as e:
    print("An error occurred:", e)

# Extract product information
tabs = json_data.get("tabs", [])
# if not tabs:
#     print(f"No more products found on page {page_number}. Ending scrape.")
# #  break

for tab in tabs:
    product_info = tab.get("product_info", {})
    product_list = product_info.get("products", [])

    for product in product_list:
        product_details = {
            "product_id": product.get("id"),
            "product_desc": product.get("desc"),
            "magnitude": product.get("magnitude"),
            "product_weight": product.get("w"),
            "unit": product.get("unit"),
            "product_USP": product.get("usp"),
            "MRP": product.get("pricing", {}).get("discount", {}).get("mrp", "0.00"),
            "MRP_per_pack" : product.get("pricing", {}).get("discount", {}).get("mrp_per_pack", "null1"),
            "selling_price": product.get("pricing", {}).get("discount", {}).get("prim_price", {}).get("sp", "0.00"),
            "sp_per_pack" : product.get("pricing", {}).get("discount", {}).get("prim_price", {}).get("sp_per_pack", "null1"), 
            "base_price": product.get("pricing", {}).get("discount", {}).get("prim_price", {}).get("base_price", "0.00"),
            "base_unit" : product.get("pricing", {}).get("discount", {}).get("prim_price", {}).get("base_unit", "null1"),
            "subscription_price" : product.get("pricing", {}).get("discount").get("subscription_price", "0.00"),
            "brand": product.get("brand", {}).get("name", ""),           
            "main_category": product.get("category", {}).get("tlc_name"),
            "sub_category1": product.get("category", {}).get("mlc_name"),
            "sub_category2": product.get("category", {}).get("llc_name"),
            "children" : "N"
            
        }
        
        all_product_details.append(product_details)
        
        # Extract details for each child product
        for child in product.get("children", []):
            
            child_details = {
            "product_id": child.get("id"),
            "product_desc": child.get("desc"),
            "magnitude": child.get("magnitude", ""),
            "product_weight": child.get("w"),
            "unit": child.get("unit", ""),
            "product_USP": child.get("usp"),
            "MRP": child.get("pricing", {}).get("discount", {}).get("mrp", "0.00"),
            "MRP_per_pack": child.get("pricing", {}).get("discount", {}).get("mrp_per_pack", "null1"),
            "selling_price": child.get("pricing", {}).get("discount", {}).get("prim_price", {}).get("sp", "0.00"),
            "sp_per_pack": child.get("pricing", {}).get("discount", {}).get("prim_price", {}).get("sp_per_pack", "null1"),
            "base_price": child.get("pricing", {}).get("discount", {}).get("prim_price", {}).get("base_price", "0.00"),
            "base_unit": child.get("pricing", {}).get("discount", {}).get("prim_price", {}).get("base_unit", "null1"),
            "subscription_price": child.get("pricing", {}).get("discount", {}).get("subscription_price", "0.00"),
            "brand": child.get("brand", {}).get("name", ""),
            "main_category": child.get("category", {}).get("tlc_name"),
            "sub_category1": child.get("category", {}).get("mlc_name"),
            "sub_category2": child.get("category", {}).get("llc_name"),
            "children": "Y"
            }
            
            all_product_details.append(child_details)


print("products:", len(all_product_details))
# Increment page number to fetch the next page
# page_number += 1
