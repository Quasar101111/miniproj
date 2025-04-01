import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Set up the WebDriver (e.g., Chrome)
chrome_driver_path = "D:/django/edit 2/chromedriver-win64/chromedriver.exe"  # Update with actual path
driver = webdriver.Chrome(executable_path=chrome_driver_path)
logger.info("WebDriver initialized successfully.")

# Open the base URL
driver.get("http://127.0.0.1:8000/inventory/insert_data/26/")
logger.info("Opened base URL.")

# Wait for the page to load
time.sleep(2)

def test_insert_inventory():
    logger.info("Running test: Insert Inventory Data")
    
    # Fill Zone details
    driver.find_element(By.ID, "zone_name").click()
    time.sleep(1)
    driver.find_element(By.ID, "zone_name").send_keys("testt")
    time.sleep(1)
    driver.find_element(By.ID, "zone_type").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "#zone_type > option:nth-child(2)").click()
    time.sleep(1)
    driver.find_element(By.ID, "zone_length").send_keys("1")
    time.sleep(1)
    driver.find_element(By.ID, "zone_breadth").send_keys("1")
    time.sleep(1)
    driver.find_element(By.ID, "zone_height").send_keys("1")
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(9)").click()
    time.sleep(1)

    # Fill Item details
    driver.find_element(By.ID, "item-tab").click()
    time.sleep(1)
    driver.find_element(By.ID, "item_name").send_keys("textile")
    time.sleep(1)
    driver.find_element(By.ID, "item_length").send_keys(".4")
    time.sleep(1)
    driver.find_element(By.ID, "item_width").send_keys(".2")
    time.sleep(1)
    driver.find_element(By.ID, "item_height").send_keys(".2")
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".btn-success").click()
    time.sleep(1)

    # Fill Location details
    driver.find_element(By.ID, "location-tab").click()
    time.sleep(1)
    driver.find_element(By.ID, "location_zone").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "#location_zone > option:nth-child(2)").click()
    time.sleep(1)
    driver.find_element(By.ID, "location_item").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "#location_item > option:nth-child(2)").click()
    time.sleep(1)
    driver.find_element(By.ID, "location_length").send_keys(".8")
    time.sleep(1)
    driver.find_element(By.ID, "location_width").send_keys(".8")
    time.sleep(1)
    driver.find_element(By.ID, "location_height").send_keys(".8")
    time.sleep(1)
    driver.find_element(By.ID, "max_stacking_height").send_keys(".8")
    time.sleep(1)
    driver.find_element(By.ID, "item_count").send_keys("31")
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".btn-warning").click()
    time.sleep(1)

# Run test
test_insert_inventory()

# Close the browser
driver.quit()
logger.info("Browser closed.")
