from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run headless Chrome

# Specify the path to the ChromeDriver executable
chrome_driver_path = 'C:/WebDriver/chromedriver-win64/chromedriver.exe'  # Update this path

# Set up the Selenium WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL to scrape
url = 'https://www.bigbasket.com/listing-svc/v2/products?type=pc&slug=apparel&page=1'

try:
    # Navigate to the URL
    driver.get(url)

    # Get the page source, which contains the JSON data
    page_source = driver.page_source

    # Extract the JSON data from the page source
    start_index = page_source.find('{')
    end_index = page_source.rfind('}') + 1
    json_data = page_source[start_index:end_index]

    # Parse the JSON data
    data = json.loads(json_data)
    print(json.dumps(data, indent=4))

except Exception as e:
    print("An error occurred:", e)

finally:
    # Close the driver
    driver.quit()
