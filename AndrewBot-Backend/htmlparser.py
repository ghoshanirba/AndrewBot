from bs4 import BeautifulSoup
import requests
import json
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.bigbasket.com',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie' : 'x-entry-context-id=100; x-entry-context=bb-b2c; _bb_locSrc=default; x-channel=web; _bb_loid=j:null; _bb_bhid=; _bb_nhid=1723; _bb_vid=MTI3MTYyMjAwNjE=; _bb_dsevid=; _bb_dsid=; csrftoken=8oxjDnGDIhO9WMm3I8GyzVlj8as0SPmwTHtIqqr2LZlE6Ch5WnS3ExUFUltJGS69; _bb_home_cache=dd66856c.1.visitor; bb2_enabled=true; ufi=1; bigbasket.com=0591c50b-5f4f-4650-8ac4-fba1f789fbe3; _gcl_au=1.1.1389406266.1720768559; jarvis-id=82654d75-d81f-4b8e-b147-77eaef4e66b5; _bb_tc=0; _bb_rdt="MzEwNDYxMDgwMw==.0"; _bb_rd=6; fs_uid=#11EGJ5#6039797689561088:9204439023068453163:::#/1752304567; adb=0; _gid=GA1.2.1009321565.1723119188; _client_version=2789; _bb_lat_long=MTIuOTQ5MTU4OTA3MXw3Ny41NzQwMjI2NzMx; _bb_hid=7427; BBAUTHTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjaGFmZiI6IjZfcTlIUHhkS3pra2xnIiwidGltZSI6MTcyMzE3OTc0NS4xMTY5NTkzLCJtaWQiOjYwMjY2NTA0LCJ2aWQiOjk5MDE4Mzg5NjMsImRldmljZV9pZCI6IldFQiIsInNvdXJjZV9pZCI6MSwiZWNfbGlzdCI6WzMsNCwxMCwxMiwxMywxNCwxNSwxNiwxNywyMCwxMDBdLCJURExUT0tFTiI6ImJjN2MyZjNkLThiMWItNDBmMy1hY2VmLWQwZTQxODFmZjM5ZCIsInJlZnJlc2hfdG9rZW4iOiI1OWNmYTgwYi0wZTc5LTRmMmItOTdiZS0zODA4ZTBjMjQxYTQiLCJ0ZGxfZXhwaXJ5IjoxNzIzNzg0NTQ0LCJleHAiOjE3Mzg5NTk3NDUsImlzX3NhZSI6bnVsbCwiZGV2aWNlX21vZGVsIjoiV0VCIiwiZGV2aWNlX2lzX2RlYnVnIjoiZmFsc2UifQ.4VTofu9_B9xKlDpGwHSpOtnhTEYqF1zi64j0YBWucyY; _bb_mid="MzA5Mjc0NzQ5NA=="; sessionid=4k6fwk0n9u845sc95yomlrltxu51yx1w; _bb_bb2.0=1; is_global=0; _bb_addressinfo=; _bb_pin_code=; _bb_sa_ids=10179; _is_bb1.0_supported=0; _bb_cda_sa_info=djIuY2RhX3NhLjEwMC4xMDE3OQ==; is_integrated_sa=0; _bb_visaddr=; _gcl_gs=2.1.k1$i1723182717; _gac_UA-27455376-1=1.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _gcl_aw=GCL.1723182724.CjwKCAjw2dG1BhB4EiwA998cqFGK4WRIFqgCFwBUzpEv9LVOJoVx9VLhjUKaPcmuhVxkCcb8tq2bdBoCDhMQAvD_BwE; _bb_cid=1; _is_tobacco_enabled=0; ts="2024-08-10 10:35:22.023"; _bb_aid="Mjg3MTIxMjQ3NQ=="; _ga=GA1.2.1996715233.1720768560; csurftoken=Qd6-bA.MTI3MTYyMjAwNjE=.1723266382657.uO3Vgzz1AUuQdPoCUxa+tpRqqc7N1t1koZ0cf+zJEds=; _ga_FRRYG5VKHX=GS1.1.1723262868.12.1.1723266805.59.0.0'
}

URL = "https://www.bigbasket.com/pd/40299874"
# Sample HTML input

try:
    # Send the GET request to the URL
    response = requests.get(URL,headers=HEADERS)
    print("response:", response)
    response.raise_for_status()  # Check for HTTP errors

    # Parse the HTML with Beautiful Soup
    html_content = response.text
    # Write HTML content to a text file
    # with open('html_content.txt', 'w', encoding='utf-8') as file:
    #     file.write(html_content)

    # print("HTML content has been written to 'html_content.txt'.")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the <script> tag with id="__NEXT_DATA__"
    script_tag = soup.find('script', id='__NEXT_DATA__')

    if script_tag:
        word_list = ['<script id="__NEXT_DATA__" type="application/json">', '</script>']
        # Extract the JSON content from the script tag
        script_tag_temp = str(script_tag)
        script_tag_temp = script_tag_temp.replace('<script id="__NEXT_DATA__" type="application/json">', '')
        json_content = script_tag_temp.replace('</script>', '')
        
        # with open('html_content.txt', 'w', encoding='utf-8') as file:
        #     file.write(json_content)
        # Parse the JSON content
        data = json.loads(json_content)
        
        # Output the JSON content to a file
        with open('data_40299874.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        children = data.get("props").get("pageProps").get("productDetails").get("children")
        print("children len:", len(children))
        for child in children:
            id = child.get("id")
            tabs = child.get("tabs")
            
            for tab in tabs:
                title = tab.get("title")
                content = tab.get("content")
                
                if title == "About the Product":
                    break
            #item_description = data.get("props").get("pageProps").get("productDetails").get("children").get("tabs")
            print("id:", id)
            
            soup = BeautifulSoup(content, 'html.parser')
            # paragraphs = soup.find_all('p')
            paragraphs = soup.get_text().strip()
            print("paragraphs:", paragraphs)
            # Extract text from each paragraph
        #     text_list = []
        #     for paragraph in paragraphs:
        #         text_list.append(paragraph.get_text(strip=True))  # strip removes leading/trailing whitespace

        # # Print the extracted text
        #     print("item description:",text_list)
        # Print a summary or part of the data if needed
        print("JSON data extracted and written to 'data.json'.")
        # You can print some part of the data to inspect it
        #print(json.dumps(data, indent=2)[:500])  # Print first 500 characters of the JSON for inspection

    else:
        print("Script tag with id '__NEXT_DATA__' not found.")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except json.JSONDecodeError as e:
    print(f"An error occurred while parsing JSON: {e}")
