import logging
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Setup Chrome with options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

try:
    # Set up the WebDriver with specific path
    chrome_driver_path = "D:/S9/miniproject/edit 2/chromedriver-win64/chromedriver.exe"
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    logger.info("WebDriver initialized successfully.")

    # Target URL
    url = "https://www.99acres.com/warehouse-for-rent-in-kerala-ffid"
    driver.get(url)
    logger.info("Opened target URL.")

    time.sleep(5)

    # Scroll down
    for _ in range(5):
        driver.execute_script("window.scrollBy(0,1000);")
        time.sleep(2)

    # Extract listings
    listings = driver.find_elements(By.CLASS_NAME, "srpTuple__tupleDetails")
    logger.info(f"Found {len(listings)} listings")

    # Store data
    data = []
    for listing in listings:
        try:
            property_type_location = listing.find_element(By.CLASS_NAME, "tupleNew__propType").text.strip()
        except:
            property_type_location = "N/A"

        try:
            price = listing.find_element(By.CLASS_NAME, "tupleNew__priceValWrap").find_element(By.TAG_NAME, "span").text.strip()
        except:
            price = "N/A"

        try:
            area = listing.find_element(By.CLASS_NAME, "tupleNew__area1Type").text.strip()
        except:
            area = "N/A"

        data.append([property_type_location, price, area])

    # Print first entry
    if data:
        print("\nFirst Property Details:")
        print(f"Property Type & Location: {data[0][0]}")
        print(f"Price: {data[0][1]}")
        print(f"Area: {data[0][2]}\n")
    else:
        print("No data was collected")

    # Save to CSV with absolute path
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "99acres_warehouse_rentals.csv")
    df = pd.DataFrame(data, columns=["Property Type & Location", "Price", "Area"])
    df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Data saved to: {output_path}")

except Exception as e:
    logger.error(f"An error occurred: {str(e)}")

finally:
    # Close browser
    if 'driver' in locals():
        driver.quit()
        logger.info("Browser closed.")