import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Setup Chrome with options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Initialize WebDriver with local ChromeDriver path
chrome_driver_path = "D:/django/edit 2/chromedriver-win64/chromedriver.exe"
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
logger.info("WebDriver initialized successfully.")

# Target 99acres URL for warehouse rentals in Kerala
url = "https://www.99acres.com/warehouse-for-rent-in-kerala-ffid"
driver.get(url)
logger.info("Opened target URL.")

# Allow page to load
time.sleep(5)

# Scroll down to load more listings
for _ in range(5):  # Adjust the number of scrolls
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(3)

# Extract listing elements
listings = driver.find_elements(By.CLASS_NAME, "srpTuple__tupleDetails")
logger.info(f"Found {len(listings)} listings")

# Store extracted data
data = []
for listing in listings:
    try:
        location = listing.find_element(By.CLASS_NAME, "tupleNew__locationName").text.strip()
    except:
        location = "N/A"

    try:
        price = listing.find_element(By.CLASS_NAME, "tupleNew__priceValWrap span:nth-of-type(1)").text.strip()
    except:
        price = "N/A"

    try:
        area = listing.find_element(By.CLASS_NAME, "tupleNew__area1Type").text.strip()
    except:
        area = "N/A"

    data.append([location, price, area])

# Save data to CSV
df = pd.DataFrame(data, columns=["Location", "Price", "Area"])
df.to_csv("99acres_warehouse_rentals.csv", index=False, encoding="utf-8")
logger.info("Data successfully saved to 99acres_warehouse_rentals.csv")

# Close the browser
driver.quit()
logger.info("Browser closed.")
