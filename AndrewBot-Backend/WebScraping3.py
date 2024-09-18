import random
import time
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

# Base URL to scrape
BASE_URL = (
    "https://www.bigbasket.com/listing-svc/v2/products?type=pc&slug=fruits-vegetables"
)

BASE_URL_PRODUCT = "https://www.bigbasket.com/pd"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.bigbasket.com",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": 'x-entry-context-id=100; x-entry-context=bb-b2c; _bb_locSrc=default; x-channel=web; _bb_loid=j:null; _bb_bhid=; _bb_nhid=1723; _bb_vid=MTI3MTYyMjAwNjE=; _bb_dsevid=; _bb_dsid=; csrftoken=8oxjDnGDIhO9WMm3I8GyzVlj8as0SPmwTHtIqqr2LZlE6Ch5WnS3ExUFUltJGS69; _bb_home_cache=dd66856c.1.visitor; bb2_enabled=true; ufi=1; bigbasket.com=0591c50b-5f4f-4650-8ac4-fba1f789fbe3; _gcl_au=1.1.1389406266.1720768559; jarvis-id=82654d75-d81f-4b8e-b147-77eaef4e66b5; _bb_tc=0; _bb_rdt="MzEwNDYxMDgwMw==.0"; _bb_rd=6; fs_uid=#11EGJ5#6039797689561088:9204439023068453163:::#/1752304567; adb=0; _gid=GA1.2.1009321565.1723119188; _client_version=2789; _bb_lat_long=MTIuOTQ5MTU4OTA3MXw3Ny41NzQwMjI2NzMx; _bb_hid=7427; BBAUTHTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjaGFmZiI6IjZfcTlIUHhkS3pra2xnIiwidGltZSI6MTcyMzE3OTc0NS4xMTY5NTkzLCJtaWQiOjYwMjY2NTA0LCJ2aWQiOjk5MDE4Mzg5NjMsImRldmljZV9pZCI6IldFQiIsInNvdXJjZV9pZCI6MSwiZWNfbGlzdCI6WzMsNCwxMCwxMiwxMywxNCwxNSwxNiwxNywyMCwxMDBdLCJURExUT0tFTiI6ImJjN2MyZjNkLThiMWItNDBmMy1hY2VmLWQwZTQxODFmZjM5ZCIsInJlZnJlc2hfdG9rZW4iOiI1OWNmYTgwYi0wZTc5LTRmMmItOTdiZS0zODA4ZTBjMjQxYTQiLCJ0ZGxfZXhwaXJ5IjoxNzIzNzg0NTQ0LCJleHAiOjE3Mzg5NTk3NDUsImlzX3NhZSI6bnVsbCwiZGV2aWNlX21vZGVsIjoiV0VCIiwiZGV2aWNlX2lzX2RlYnVnIjoiZmFsc2UifQ.4VTofu9_B9xKlDpGwHSpOtnhTEYqF1zi64j0YBWucyY; _bb_mid="MzA5Mjc0NzQ5NA=="; sessionid=4k6fwk0n9u845sc95yomlrltxu51yx1w; _bb_bb2.0=1; is_global=0; _bb_addressinfo=; _bb_pin_code=; _bb_sa_ids=10179; _is_bb1.0_supported=0; _bb_cda_sa_info=djIuY2RhX3NhLjEwMC4xMDE3OQ==; is_integrated_sa=0; _bb_visaddr=; _gcl_gs=2.1.k1$i1723182717; _gac_UA-27455376-1=1.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _gcl_aw=GCL.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _bb_cid=1; _bb_aid="Mjg3MTIxMjQ3NQ=="; _is_tobacco_enabled=0; _ga=GA1.1.1996715233.1720768560; _ga_FRRYG5VKHX=GS1.1.1723299484.13.1.1723300136.54.0.0; ts="2024-08-10 19:58:56.564"; csurftoken=DIK3ag.MTI3MTYyMjAwNjE=.1723301381051.63PNIWWdibwGxZrzhOM2EFD36geFHWjVnCQhr1XIoN8=',
}

HEADERS_PRODUCT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.bigbasket.com",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": 'x-entry-context-id=100; x-entry-context=bb-b2c; _bb_locSrc=default; x-channel=web; _bb_loid=j:null; _bb_bhid=; _bb_nhid=1723; _bb_vid=MTI3MTYyMjAwNjE=; _bb_dsevid=; _bb_dsid=; csrftoken=8oxjDnGDIhO9WMm3I8GyzVlj8as0SPmwTHtIqqr2LZlE6Ch5WnS3ExUFUltJGS69; _bb_home_cache=dd66856c.1.visitor; bb2_enabled=true; ufi=1; bigbasket.com=0591c50b-5f4f-4650-8ac4-fba1f789fbe3; _gcl_au=1.1.1389406266.1720768559; jarvis-id=82654d75-d81f-4b8e-b147-77eaef4e66b5; _bb_tc=0; _bb_rdt="MzEwNDYxMDgwMw==.0"; _bb_rd=6; fs_uid=#11EGJ5#6039797689561088:9204439023068453163:::#/1752304567; adb=0; _gid=GA1.2.1009321565.1723119188; _client_version=2789; _bb_lat_long=MTIuOTQ5MTU4OTA3MXw3Ny41NzQwMjI2NzMx; _bb_hid=7427; BBAUTHTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjaGFmZiI6IjZfcTlIUHhkS3pra2xnIiwidGltZSI6MTcyMzE3OTc0NS4xMTY5NTkzLCJtaWQiOjYwMjY2NTA0LCJ2aWQiOjk5MDE4Mzg5NjMsImRldmljZV9pZCI6IldFQiIsInNvdXJjZV9pZCI6MSwiZWNfbGlzdCI6WzMsNCwxMCwxMiwxMywxNCwxNSwxNiwxNywyMCwxMDBdLCJURExUT0tFTiI6ImJjN2MyZjNkLThiMWItNDBmMy1hY2VmLWQwZTQxODFmZjM5ZCIsInJlZnJlc2hfdG9rZW4iOiI1OWNmYTgwYi0wZTc5LTRmMmItOTdiZS0zODA4ZTBjMjQxYTQiLCJ0ZGxfZXhwaXJ5IjoxNzIzNzg0NTQ0LCJleHAiOjE3Mzg5NTk3NDUsImlzX3NhZSI6bnVsbCwiZGV2aWNlX21vZGVsIjoiV0VCIiwiZGV2aWNlX2lzX2RlYnVnIjoiZmFsc2UifQ.4VTofu9_B9xKlDpGwHSpOtnhTEYqF1zi64j0YBWucyY; _bb_mid="MzA5Mjc0NzQ5NA=="; sessionid=4k6fwk0n9u845sc95yomlrltxu51yx1w; _bb_bb2.0=1; is_global=0; _bb_addressinfo=; _bb_pin_code=; _bb_sa_ids=10179; _is_bb1.0_supported=0; _bb_cda_sa_info=djIuY2RhX3NhLjEwMC4xMDE3OQ==; is_integrated_sa=0; _bb_visaddr=; _gcl_gs=2.1.k1$i1723182717; _gac_UA-27455376-1=1.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _gcl_aw=GCL.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _bb_cid=1; _is_tobacco_enabled=0; ts="2024-08-10 10:35:22.023"; _bb_aid="Mjg3MTIxMjQ3NQ=="; _ga=GA1.2.1996715233.1720768560; csurftoken=Qd6-bA.MTI3MTYyMjAwNjE=.1723266382657.uO3Vgzz1AUuQdPoCUxa+tpRqqc7N1t1koZ0cf+zJEds=; _ga_FRRYG5VKHX=GS1.1.1723262868.12.1.1723266805.59.0.0',
}


def fetch_multi_product_data(page_number):
    # Fetch product data from a given page number.
    url = f"{BASE_URL}&page={page_number}"
    print("URL:", url)
    try:
        response = requests.get(url, headers=HEADERS)
        json_data = json.loads(response.text)
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def fetch_single_product_data(product_id):
    # Fetch product data from a given product ID.
    url = f"{BASE_URL_PRODUCT}/{product_id}"

    try:
        response = requests.get(url, headers=HEADERS_PRODUCT)
        response.raise_for_status()  # Check for HTTP errors

        # Parse the HTML with Beautiful Soup
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the <script> tag with id="__NEXT_DATA__"
        script_tag = soup.find("script", id="__NEXT_DATA__")

        if script_tag:
            # Extract the JSON content from the script tag
            script_tag_temp = str(script_tag)
            script_tag_temp = script_tag_temp.replace(
                '<script id="__NEXT_DATA__" type="application/json">', ""
            )
            json_content = script_tag_temp.replace("</script>", "")
            # Parse the JSON content
            json_data = json.loads(json_content)
            return json_data
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_about_the_product(tabs):

    for tab in tabs:
        title = tab.get("title")
        content = tab.get("content")

        if title.strip() == "About the Product":
            break

        soup = BeautifulSoup(content, "html.parser")
        paragraphs = soup.get_text().strip()

        if paragraphs:
            return paragraphs
        else:
            return " "


def parse_products(main_product_id, json_data, mlc_name, main_product_flag):
    # Parse product data from JSON response.
    all_product_details = []
    print("within parse_products method, main_product_id:", main_product_id)
    children = (
        json_data.get("props", {})
        .get("pageProps", {})
        .get("productDetails", {})
        .get("children", [])
    )

    for child in children:

        product_id = child.get("id")

        if product_id == main_product_id:
            child_flag = "N"
        else:
            child_flag = "Y"

        # product_desc = child.get("desc")
        # product_weight = child.get("w")

        all_product_details.append(
            {
                "product_id": product_id,
                "product_desc": child.get("desc"),
                # "magnitude": child.get("magnitude"),
                "product_weight": child.get("w"),
                # "unit": child.get("unit"),
                "product_USP": child.get("usp"),
                "brand": child.get("brand").get("name"),
                "main_category": child.get("category", {}).get("tlc_name"),
                "sub_category1": mlc_name,
                "sub_category2": child.get("category", {}).get("llc_name"),
                "MRP": child.get("pricing", {}).get("discount", {}).get("mrp", "0.00"),
                # "MRP_per_pack": child.get("pricing", {})
                # .get("discount", {})
                # .get("mrp_per_pack", "null1"),
                "selling_price": child.get("pricing", {})
                .get("discount", {})
                .get("prim_price", {})
                .get("sp", "0.00"),
                # "sp_per_pack": child.get("pricing", {})
                # .get("discount", {})
                # .get("prim_price", {})
                # .get("sp_per_pack", "null1"),
                "base_price": child.get("pricing", {})
                .get("discount", {})
                .get("prim_price", {})
                .get("base_price", "0.00"),
                "base_unit": child.get("pricing", {})
                .get("discount", {})
                .get("prim_price", {})
                .get("base_unit", "null1"),
                # "subscription_price": child.get("pricing", {})
                # .get("discount")
                # .get("subscription_price", "0.00"),
                # "brand": child.get("brand", {}).get("name", ""),
                "avg_rating": child.get("rating_info", {}).get("avg_rating"),
                "children": child_flag,
                "about_the_product": get_about_the_product(child.get("tabs", [])),
            }
        )

        # all_product_details.append(
        #     {
        #         "product_id": product_id,
        #         "desc": product_desc,
        #         "weight": product_weight,
        #         "mlc_name": mlc_name,
        #         "child": child_flag,
        #     }
        # )

        # child_children = child.get("children", [])

        # for child_child in child_children:
        #     child_product_id = child_child.get("id")
        #     child_product_desc = child_child.get("desc")
        #     child_product_weight = child_child.get("w")
        #     all_product_details.append(
        #         {
        #             "product_id": child_product_id,
        #             "desc": child_product_desc,
        #             "weight": child_product_weight,
        #             "mlc_name": mlc_name,
        #             "child": "Y"
        #         }
        #     )

    return all_product_details


def extract_product_details(product, is_child):
    """Extract details from a product."""
    return {
        "product_id": product.get("id"),
        "product_desc": product.get("desc"),
        "magnitude": product.get("magnitude"),
        "product_weight": product.get("w"),
        "unit": product.get("unit"),
        "product_USP": product.get("usp"),
        "MRP": product.get("pricing", {}).get("discount", {}).get("mrp", "0.00"),
        "MRP_per_pack": product.get("pricing", {})
        .get("discount", {})
        .get("mrp_per_pack", "null1"),
        "selling_price": product.get("pricing", {})
        .get("discount", {})
        .get("prim_price", {})
        .get("sp", "0.00"),
        "sp_per_pack": product.get("pricing", {})
        .get("discount", {})
        .get("prim_price", {})
        .get("sp_per_pack", "null1"),
        "base_price": product.get("pricing", {})
        .get("discount", {})
        .get("prim_price", {})
        .get("base_price", "0.00"),
        "base_unit": product.get("pricing", {})
        .get("discount", {})
        .get("prim_price", {})
        .get("base_unit", "null1"),
        "subscription_price": product.get("pricing", {})
        .get("discount")
        .get("subscription_price", "0.00"),
        "brand": product.get("brand", {}).get("name", ""),
        "main_category": product.get("category", {}).get("tlc_name"),
        "sub_category1": product.get("category", {}).get("mlc_name"),
        "sub_category2": product.get("category", {}).get("llc_name"),
        "avg_rating": product.get("rating_info", {}).get("avg_rating"),
        "children": is_child,
    }


def save_to_csv(data, filename):
    """Save the product data to a CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")


def fetch_main_product_ids(json_data):
    main_product_id_list = []
    tabs = json_data.get("tabs", [])

    for tab in tabs:
        product_info = tab.get("product_info", {})
        product_list = product_info.get("products", [])

        for product in product_list:
            product_id = product.get("id")
            mlc_name = product.get("category").get("mlc_name")
            main_product_flag = "Y"

            main_product_id_list.append(
                {
                    "product_id": product_id,
                    "mlc_name": mlc_name,
                    "main_product_flag": main_product_flag,
                }
            )

    return main_product_id_list


def main():
    page_number = 1
    hold_json_data = {}
    all_product_details = []
    main_product_id_list = []

    json_data = fetch_multi_product_data(page_number)

    if json_data:
        main_product_id_list = fetch_main_product_ids(json_data)
    else:
        print(f"No data received for page {page_number}. Ending scrape.")

    print("count of main product IDs:", len(main_product_id_list))

    for main_product_id in main_product_id_list:
        # main_product_id_json = json.loads(main_product_id)
        product_id = main_product_id.get("product_id")
        mlc_name = main_product_id.get("mlc_name")
        main_product_flag = main_product_id.get("main_product_flag")
        single_product_json_data = fetch_single_product_data(product_id)

        if single_product_json_data:
            all_product_details = parse_products(
                product_id, single_product_json_data, mlc_name, main_product_flag
            )
            # print("all_product_details:", all_product_details)

            save_to_csv(all_product_details, 'products.csv')
             
        random_integer = random.randint(5, 10)
        time.sleep(random_integer)


if __name__ == "__main__":
    main()
