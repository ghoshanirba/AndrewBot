import random
import time
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

# Base URL to scrape
# BASE_URL = (
#     "https://www.bigbasket.com/listing-svc/v2/products?type=pc&slug=fruits-vegetables"
# )

BASE_URL = (
    "https://www.bigbasket.com/listing-svc/v2/products?type=pc&slug=gourmet-world-food"
)

BASE_URL_PRODUCT = "https://www.bigbasket.com/pd"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.bigbasket.com",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": 'x-entry-context-id=100; x-entry-context=bb-b2c; _bb_locSrc=default; x-channel=web; _bb_loid=j:null; _bb_bhid=; _bb_nhid=1723; _bb_vid=MTI3MTYyMjAwNjE=; _bb_dsevid=; _bb_dsid=; csrftoken=8oxjDnGDIhO9WMm3I8GyzVlj8as0SPmwTHtIqqr2LZlE6Ch5WnS3ExUFUltJGS69; _bb_home_cache=dd66856c.1.visitor; bb2_enabled=true; ufi=1; bigbasket.com=0591c50b-5f4f-4650-8ac4-fba1f789fbe3; _gcl_au=1.1.1389406266.1720768559; jarvis-id=82654d75-d81f-4b8e-b147-77eaef4e66b5; _bb_tc=0; _bb_rdt="MzEwNDYxMDgwMw==.0"; _bb_rd=6; fs_uid=#11EGJ5#6039797689561088:9204439023068453163:::#/1752304567; adb=0; _gid=GA1.2.1009321565.1723119188; _client_version=2789; _bb_lat_long=MTIuOTQ5MTU4OTA3MXw3Ny41NzQwMjI2NzMx; _bb_hid=7427; BBAUTHTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjaGFmZiI6IjZfcTlIUHhkS3pra2xnIiwidGltZSI6MTcyMzE3OTc0NS4xMTY5NTkzLCJtaWQiOjYwMjY2NTA0LCJ2aWQiOjk5MDE4Mzg5NjMsImRldmljZV9pZCI6IldFQiIsInNvdXJjZV9pZCI6MSwiZWNfbGlzdCI6WzMsNCwxMCwxMiwxMywxNCwxNSwxNiwxNywyMCwxMDBdLCJURExUT0tFTiI6ImJjN2MyZjNkLThiMWItNDBmMy1hY2VmLWQwZTQxODFmZjM5ZCIsInJlZnJlc2hfdG9rZW4iOiI1OWNmYTgwYi0wZTc5LTRmMmItOTdiZS0zODA4ZTBjMjQxYTQiLCJ0ZGxfZXhwaXJ5IjoxNzIzNzg0NTQ0LCJleHAiOjE3Mzg5NTk3NDUsImlzX3NhZSI6bnVsbCwiZGV2aWNlX21vZGVsIjoiV0VCIiwiZGV2aWNlX2lzX2RlYnVnIjoiZmFsc2UifQ.4VTofu9_B9xKlDpGwHSpOtnhTEYqF1zi64j0YBWucyY; _bb_mid="MzA5Mjc0NzQ5NA=="; sessionid=4k6fwk0n9u845sc95yomlrltxu51yx1w; _bb_bb2.0=1; is_global=0; _bb_addressinfo=; _bb_pin_code=; _bb_sa_ids=10179; _is_bb1.0_supported=0; _bb_cda_sa_info=djIuY2RhX3NhLjEwMC4xMDE3OQ==; is_integrated_sa=0; _bb_visaddr=; _gcl_gs=2.1.k1$i1723182717; _gac_UA-27455376-1=1.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _gcl_aw=GCL.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _bb_cid=1; _bb_aid="Mjg3MTIxMjQ3NQ=="; csurftoken=3XqvxA.MTI3MTYyMjAwNjE=.1723698343552.jG/A5IFr/Yy6mjR1KOwotwrK2gEH2NvozlZoZTawwBE=; _gat_UA-27455376-1=1; _ga_FRRYG5VKHX=GS1.1.1723698355.38.1.1723698370.45.0.0; _ga=GA1.2.1996715233.1720768560; _is_tobacco_enabled=0; ts="2024-08-15 10:36:11.880"',
}

HEADERS_PRODUCT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.bigbasket.com",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": 'x-entry-context-id=100; x-entry-context=bb-b2c; _bb_locSrc=default; x-channel=web; _bb_loid=j:null; _bb_bhid=; _bb_nhid=1723; _bb_vid=MTI3MTYyMjAwNjE=; _bb_dsevid=; _bb_dsid=; csrftoken=8oxjDnGDIhO9WMm3I8GyzVlj8as0SPmwTHtIqqr2LZlE6Ch5WnS3ExUFUltJGS69; _bb_home_cache=dd66856c.1.visitor; bb2_enabled=true; ufi=1; bigbasket.com=0591c50b-5f4f-4650-8ac4-fba1f789fbe3; _gcl_au=1.1.1389406266.1720768559; jarvis-id=82654d75-d81f-4b8e-b147-77eaef4e66b5; _bb_tc=0; _bb_rdt="MzEwNDYxMDgwMw==.0"; _bb_rd=6; fs_uid=#11EGJ5#6039797689561088:9204439023068453163:::#/1752304567; adb=0; _gid=GA1.2.1009321565.1723119188; _client_version=2789; _bb_lat_long=MTIuOTQ5MTU4OTA3MXw3Ny41NzQwMjI2NzMx; _bb_hid=7427; BBAUTHTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjaGFmZiI6IjZfcTlIUHhkS3pra2xnIiwidGltZSI6MTcyMzE3OTc0NS4xMTY5NTkzLCJtaWQiOjYwMjY2NTA0LCJ2aWQiOjk5MDE4Mzg5NjMsImRldmljZV9pZCI6IldFQiIsInNvdXJjZV9pZCI6MSwiZWNfbGlzdCI6WzMsNCwxMCwxMiwxMywxNCwxNSwxNiwxNywyMCwxMDBdLCJURExUT0tFTiI6ImJjN2MyZjNkLThiMWItNDBmMy1hY2VmLWQwZTQxODFmZjM5ZCIsInJlZnJlc2hfdG9rZW4iOiI1OWNmYTgwYi0wZTc5LTRmMmItOTdiZS0zODA4ZTBjMjQxYTQiLCJ0ZGxfZXhwaXJ5IjoxNzIzNzg0NTQ0LCJleHAiOjE3Mzg5NTk3NDUsImlzX3NhZSI6bnVsbCwiZGV2aWNlX21vZGVsIjoiV0VCIiwiZGV2aWNlX2lzX2RlYnVnIjoiZmFsc2UifQ.4VTofu9_B9xKlDpGwHSpOtnhTEYqF1zi64j0YBWucyY; _bb_mid="MzA5Mjc0NzQ5NA=="; sessionid=4k6fwk0n9u845sc95yomlrltxu51yx1w; _bb_bb2.0=1; is_global=0; _bb_addressinfo=; _bb_pin_code=; _bb_sa_ids=10179; _is_bb1.0_supported=0; _bb_cda_sa_info=djIuY2RhX3NhLjEwMC4xMDE3OQ==; is_integrated_sa=0; _bb_visaddr=; _gcl_gs=2.1.k1$i1723182717; _gac_UA-27455376-1=1.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _gcl_aw=GCL.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _bb_cid=1; _bb_aid="Mjg3MTIxMjQ3NQ=="; csurftoken=3XqvxA.MTI3MTYyMjAwNjE=.1723698343552.jG/A5IFr/Yy6mjR1KOwotwrK2gEH2NvozlZoZTawwBE=; _ga_FRRYG5VKHX=GS1.1.1723698355.38.1.1723698370.45.0.0; _ga=GA1.2.1996715233.1720768560; _is_tobacco_enabled=0; ts="2024-08-15 10:36:11.880"',
}


def fetch_product_data(page_number):
    """Fetch product data from a given page number."""
    url = f"{BASE_URL}&page={page_number}"
    try:
        response = requests.get(url, headers=HEADERS)
        json_data = json.loads(response.text)
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"HTTP or Network error occurred: {e}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from the response.")
    return None


def get_products_list(json_data):
    products_list = []

    tabs = json_data.get("tabs", [])

    for tab in tabs:
        product_info = tab.get("product_info", {})
        products_list = product_info.get("products", [])
        number_of_pages = product_info.get("number_of_pages", 0)

    return products_list, number_of_pages


def parse_products(product_json_data):
    # Parse product data from JSON response.
    product_details = []
    product_descriptions = []

    # EXTRACT PRODUCT DETAILS FOR BOTH MAIN AND CHILD PRODUCT IDS USING MAIN PRODUCT ID AS DRIVER.
    # product_details list will contain product details for both main and child product IDs.
    product_details.append(extract_product_details(product_json_data, "N"))

    # Extract details for each child product
    for child in product_json_data.get("children", []):
        product_details.append(extract_product_details(child, "Y"))

    # EXTRACT PRODUCT DESCRIPTIONS USING MAIN PRODUCT ID AS DRIVER
    main_product_id = product_json_data.get("id")

    # product descriptions will contain descriptions for both main as well as child product IDs.
    product_descriptions = get_main_child_product_description(main_product_id)

    # product_descriptions.append(product_descriptions)

    return product_details, product_descriptions


def parse_product_description(product_id, json_data, main_product_flag):
    # print("within parse_product_description")
    product_descriptions = []
    paragraphs = ""

    children = (
        json_data.get("props", {})
        .get("pageProps", {})
        .get("productDetails", {})
        .get("children", [])
    )
    print("product id for description extraction:", product_id)
    # print("description children length:", len(children))
    for child in children:
        more_details = ""
        child_product_id = child.get("id")

        # print("child product_id for description:", child_product_id)

        if child_product_id == product_id:
            child_flag = "N"
        else:
            child_flag = "Y"

        tabs = child.get("tabs", [])

        for tab in tabs:
            title = tab.get("title")
            content = tab.get("content")

            # if title.strip() == "About the Product":
            soup = BeautifulSoup(content, "html.parser")
            paragraphs = title + ":" + "\n" + soup.get_text().strip() + "\n"
            more_details += paragraphs

        product_descriptions.append(
            {
                "product_id": child_product_id,
                "about_the_product": more_details,
                "children": child_flag,
            }
        )
        # "about_the_product": paragraphs,
    # print("product_descriptions:", product_descriptions)
    return product_descriptions


def get_main_child_product_description(product_id):
    # print("within get_main_child_product_description")
    # print(f"product id {product_id} received for retrieving descriptions")
    product_descriptions = []
    url = f"{BASE_URL_PRODUCT}/{product_id}"
    attempt_count = 0
    max_attempts = 10

    while attempt_count < max_attempts:
        try:
            random_integer = random.randint(5, 10)
            time.sleep(random_integer)

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
                main_product_flag = "Y"

                if json_data:
                    product_descriptions.extend(
                        parse_product_description(
                            product_id, json_data, main_product_flag
                        )
                    )
                    # print("product_descriptions:", product_descriptions)
                    return product_descriptions

            break
        except requests.exceptions.RequestException as e:
            print(f"An error occurred on attempt {attempt_count + 1}: {e}")
            attempt_count += 1
            if attempt_count >= max_attempts:
                print(
                    f"Max retries reached. Skipping this main product ID: {product_id}"
                )
                product_descriptions.append(
                    {
                        "product_id": product_id,
                        "about_the_product": "obtained server error, fill it manually",
                        "children": "N",
                    }
                )
                return product_descriptions
        except Exception as e:
            print(f"An unexpected error occurred on attempt {attempt_count + 1}: {e}")
            attempt_count += 1
            if attempt_count >= max_attempts:
                print(
                    f"Max retries reached due to unexpected errors.. Skipping this main product ID: {product_id}"
                )
                product_descriptions.append(
                    {
                        "product_id": product_id,
                        "about_the_product": "obtained unexpected error, fill it manually",
                        "children": "N",
                    }
                )
                return product_descriptions        
                # return None


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
        "discount_text": product.get("pricing", {})
        .get("discount", {})
        .get("d_text", "0.00"),
        "brand": product.get("brand", {}).get("name", ""),
        "main_category": product.get("category", {}).get("tlc_name"),
        "sub_category1": product.get("category", {}).get("mlc_name"),
        "sub_category2": product.get("category", {}).get("llc_name"),
        "avg_rating": product.get("rating_info", {}).get("avg_rating"),
        "children": is_child,
    }


def convert_product_details_description_list_to_df(
    product_details_list, product_descriptions_list
):
    # print("within convert_product_details_description_list_to_df")
    product_details_df = pd.DataFrame(product_details_list)

    # all_product_descriptions_flat_list = [
    #     item for sublist in all_product_descriptions for item in sublist
    # ]

    product_descriptions_df = pd.DataFrame(product_descriptions_list)

    # print("Product Details Columns: ", product_details_df.columns)
    # print("Product Descriptions Columns: ", product_descriptions_df.columns)
    try:
        merged_product_details_with_description_df = pd.merge(
            product_details_df,
            product_descriptions_df[["product_id", "about_the_product"]],
            on="product_id",
            how="left",
        )
    except KeyError:
        print("Key error occurred")
        print("product_details_df:", product_details_df)
        print("product_descriptions_df:", product_descriptions_df)
        print("product_descriptions_list 2:", product_descriptions_list)
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

    return merged_product_details_with_description_df


def save_to_csv(data_df, filename, firt_time_flag):

    data_df = pd.DataFrame(data_df)

    if firt_time_flag:
        # write the dataframe data along with headers into the csv file for the 1st time.
        data_df.to_csv(filename, index=False)
    else:
        # skip writing of header for next batch and append the dataframe to the csv.
        data_df.to_csv(filename, index=False, mode="a", header=False)


def main():
    start_page_number = 1
    scrape_page_count = 40
    end_page_number = start_page_number + scrape_page_count
    page_number = start_page_number
    is_firt_time = True
    filename = "product_details.csv"

    while True:
        record_count_per_page = 0
        print(f"STARTING SCRAPE FOR PAGE NUMBER {page_number}")
        json_data = fetch_product_data(page_number)

        if json_data:
            products_list, number_of_pages = get_products_list(json_data)

            for product in products_list:
                product_json_data = product
                product_details, product_descriptions = parse_products(
                    product_json_data
                )
                # print("product_descriptions:", product_descriptions)

                if not product_details:
                    print(
                        f"No more products found on page {page_number}. Ending scrape."
                    )
                    break
                else:
                    if not product_descriptions:
                        print("product_descriptions 1:", product_descriptions)

                    merged_product_details_with_description_df = (
                        convert_product_details_description_list_to_df(
                            product_details, product_descriptions
                        )
                    )
                record_count_per_page += len(merged_product_details_with_description_df)

                save_to_csv(
                    merged_product_details_with_description_df, filename, is_firt_time
                )

                is_firt_time = False
        else:
            print(f"No data received for page {page_number}. Ending scrape.")
            break

        print(
            f"Page {page_number} - Total products retrieved so far: {record_count_per_page}"
        )
        page_number += 1

        if (page_number > number_of_pages) or (page_number > end_page_number):
            break


if __name__ == "__main__":
    main()
