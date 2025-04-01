import logging
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class TestInventoryInsert(unittest.TestCase):
    def setUp(self):
        print("\n" + "="*60)
        print("STARTING TEST: Inventory Insert")
        print("="*60 + "\n")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--start-maximized')  # Start with maximized window

        # Set up the WebDriver
        chrome_driver_path = "D:/S9/miniproject/edit 2/chromedriver-win64/chromedriver.exe"
        service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # Set up explicit wait
        logger.info("WebDriver initialized successfully.")

        # Open the base URL
        self.driver.get("http://127.0.0.1:8000/inventory/insert_data/26/")
        logger.info("Opened base URL.")
        time.sleep(2)

    def scroll_to_element(self, element):
        """Scroll element into view and wait for it to be clickable"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)  # Wait for scroll to complete
        return element

    def safe_click(self, element):
        """Safely click an element with retry logic"""
        try:
            element = self.scroll_to_element(element)
            element.click()
        except Exception as e:
            # If regular click fails, try JavaScript click
            self.driver.execute_script("arguments[0].click();", element)

    def test_insert_inventory(self):
        start_time = time.time()
        try:
            print("TEST STEPS:")
            print("-"*60)
            
            # Fill Zone details
            print("[1/3] Filling Zone Details...")
            
            # Wait for and fill zone name
            zone_name = self.wait.until(EC.presence_of_element_located((By.ID, "zone_name")))
            zone_name.clear()
            zone_name.send_keys("testt")
            time.sleep(1)

            # Handle zone type selection
            zone_type = self.wait.until(EC.presence_of_element_located((By.ID, "zone_type")))
            self.safe_click(zone_type)
            time.sleep(1)
            zone_type_option = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#zone_type > option:nth-child(2)")))
            self.safe_click(zone_type_option)
            time.sleep(1)

            # Fill dimensions
            self.driver.find_element(By.ID, "zone_length").send_keys("1")
            time.sleep(1)
            self.driver.find_element(By.ID, "zone_breadth").send_keys("1")
            time.sleep(1)
            self.driver.find_element(By.ID, "zone_height").send_keys("1")
            time.sleep(1)

            # Click submit button
            submit_btn = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn:nth-child(9)")))
            self.safe_click(submit_btn)
            time.sleep(2)

            # Fill Item details
            print("[2/3] Filling Item Details...")
            item_tab = self.wait.until(EC.presence_of_element_located((By.ID, "item-tab")))
            self.safe_click(item_tab)
            time.sleep(1)

            # Fill item details
            self.driver.find_element(By.ID, "item_name").send_keys("textile")
            time.sleep(1)
            self.driver.find_element(By.ID, "item_length").send_keys(".4")
            time.sleep(1)
            self.driver.find_element(By.ID, "item_width").send_keys(".2")
            time.sleep(1)
            self.driver.find_element(By.ID, "item_height").send_keys(".2")
            time.sleep(1)

            # Click success button
            success_btn = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-success")))
            self.safe_click(success_btn)
            time.sleep(2)

            # Fill Location details
            print("[3/3] Filling Location Details...")
            location_tab = self.wait.until(EC.presence_of_element_located((By.ID, "location-tab")))
            self.safe_click(location_tab)
            time.sleep(1)

            # Handle location zone selection
            location_zone = self.wait.until(EC.presence_of_element_located((By.ID, "location_zone")))
            self.safe_click(location_zone)
            time.sleep(1)
            location_zone_option = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#location_zone > option:nth-child(2)")))
            self.safe_click(location_zone_option)
            time.sleep(1)

            # Handle location item selection
            location_item = self.wait.until(EC.presence_of_element_located((By.ID, "location_item")))
            self.safe_click(location_item)
            time.sleep(1)
            location_item_option = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#location_item > option:nth-child(2)")))
            self.safe_click(location_item_option)
            time.sleep(1)

            # Fill location details
            self.driver.find_element(By.ID, "location_length").send_keys(".8")
            time.sleep(1)
            self.driver.find_element(By.ID, "location_width").send_keys(".8")
            time.sleep(1)
            self.driver.find_element(By.ID, "location_height").send_keys(".8")
            time.sleep(1)
            self.driver.find_element(By.ID, "max_stacking_height").send_keys(".8")
            time.sleep(1)
            self.driver.find_element(By.ID, "item_count").send_keys("31")
            time.sleep(1)

            # Click warning button
            warning_btn = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-warning")))
            self.safe_click(warning_btn)
            time.sleep(2)

            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            print("\n" + "="*60)
            print("TEST RESULTS: PASSED")
            print("-"*60)
            print(f"Duration: {duration} seconds")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60 + "\n")
            
            logger.info("Test completed successfully!")
            
        except Exception as e:
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            print("\n" + "="*60)
            print("TEST RESULTS: FAILED")
            print("-"*60)
            print(f"Duration: {duration} seconds")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Error: {str(e)}")
            print("="*60 + "\n")
            
            logger.error(f"Test failed with error: {str(e)}")
            raise

    def tearDown(self):
        self.driver.quit()
        logger.info("Browser closed.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
