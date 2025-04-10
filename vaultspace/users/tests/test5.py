import logging
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class TestWarehouse(unittest.TestCase):
    def setUp(self):
        print("\n" + "="*60)
        print("STARTING TEST: Warehouse Management")
        print("="*60 + "\n")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--start-maximized')

        # Set up the WebDriver
        chrome_driver_path = "D:/S9/miniproject/edit 2/chromedriver-win64/chromedriver.exe"
        service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # Explicit wait
        logger.info("WebDriver initialized successfully.")

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

    def test_warehouse_management(self):
        start_time = time.time()
        try:
            print("TEST STEPS:")
            print("-"*60)
            
            # Login
            print("[1/7] Logging in...")
            self.driver.get("http://127.0.0.1:8000/login/")
            logger.info("Opened login page.")
            time.sleep(2)

            # Enter credentials
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            email_field.clear()
            email_field.send_keys("jhon@gmail.com")
            time.sleep(1)
            
            password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_field.clear()
            password_field.send_keys("gDSN:,pb,4u45F2")
            time.sleep(1)
            
            # Click login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            self.safe_click(login_button)
            time.sleep(2)

            # Add Warehouse
            print("[2/7] Adding Warehouse...")
            add_warehouse_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add Warehouse")))
            self.safe_click(add_warehouse_link)
            time.sleep(2)

            # First warehouse input
            print("[3/7] Entering First Warehouse Details...")
            user_input = self.wait.until(EC.presence_of_element_located((By.ID, "user-input")))
            user_input.clear()
            user_input.send_keys("30x11x14")
            user_input.send_keys(Keys.ENTER)
            time.sleep(1)

            # Fill dimensions
            self.driver.find_element(By.ID, "breadth").send_keys("11")
            self.driver.find_element(By.ID, "warehouseHeight").send_keys("14")
            time.sleep(1)

            # Second warehouse input
            print("[4/7] Entering Second Warehouse Details...")
            self.driver.execute_script("window.scrollTo(0,0)")
            user_input.clear()
            user_input.send_keys("warehouse is 20x13x16 near bus stand")
            user_input.send_keys(Keys.ENTER)
            time.sleep(1)

            # Fill second warehouse details
            self.driver.find_element(By.ID, "breadth").send_keys("13")
            self.driver.find_element(By.ID, "warehouseHeight").send_keys("16")
            self.driver.find_element(By.ID, "landmark").send_keys("Bus stand")
            time.sleep(1)

            # Set location
            print("[5/7] Setting Location...")
            self.driver.execute_script("window.scrollTo(0,0)")
            user_input.clear()
            user_input.send_keys("set location")
            user_input.send_keys(Keys.ENTER)
            time.sleep(1)

            # Handle location window
            print("[6/7] Handling Location Window...")
            location_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".alert:nth-child(13) .btn")))
            self.safe_click(location_button)
            time.sleep(2)

            # Terms and conditions
            print("[7/7] Creating Terms and Conditions...")
            user_input.clear()
            user_input.send_keys("create terms and conditions specifying lease for at least 2 months")
            user_input.send_keys(Keys.ENTER)
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
        time.sleep(5)  # Wait for 5 seconds before closing
        self.driver.quit()
        logger.info("Browser closed.")

if __name__ == '__main__':
    unittest.main(verbosity=0)
