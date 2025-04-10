import unittest
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime

class TestManageUsers(unittest.TestCase):

    def setUp(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()

        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_driver_path = "D:/S9/miniproject/edit 2/chromedriver-win64/chromedriver.exe"
        service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5)
        self.logger.info("WebDriver initialized and browser opened.")

    def login(self, username, password):
        self.driver.get("http://localhost:8000/login")
        self.logger.info("Opened login page.")
        time.sleep(1)

        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

        username_field.clear()
        password_field.clear()
        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()
        time.sleep(2)

        if "login" in self.driver.current_url:
            raise Exception(f"Login failed or user was redirected back to login. Current URL: {self.driver.current_url}")

    def test_admin_navigation(self):
        driver = self.driver
        test_passed = False
        start_time = time.time()

        try:
            self.logger.info("[Test] Starting admin dashboard navigation test...")

            # Perform login
            self.login("admin1@gmail.com", "gDSN:,pb,4u45F2")
            self.logger.info("Logged in successfully.")

            # Step 1: Open admin dashboard (use localhost to match login domain)
            driver.get("http://localhost:8000/admin_dashboard/")
            self.logger.info("Opened admin dashboard URL.")

            # Step 2: Set window size
            driver.set_window_size(1936, 1048)
            self.logger.info("Set browser window size.")

            # Step 3: Click 'Manage Lessors'
            driver.find_element(By.LINK_TEXT, "Manage Lessors").click()
            self.logger.info("Clicked 'Manage Lessors'.")
            time.sleep(1)

            # Step 4: Click 'Manage Tenants'
            driver.find_element(By.LINK_TEXT, "Manage Tenants").click()
            self.logger.info("Clicked 'Manage Tenants'.")
            time.sleep(1)

            # Step 5: Click button in second row
            driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .btn").click()
            self.logger.info("Clicked button in second table row.")
            time.sleep(2)

            test_passed = True

        except Exception as e:
            self.logger.error("Test failed due to: %s", str(e))
            raise

        finally:
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            print("\n[Test Completed]")
            print("Status: {}".format("PASSED" if test_passed else "FAILED"))
            print("Duration: {} seconds".format(duration))
            print("Timestamp: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    def tearDown(self):
        self.driver.quit()
        self.logger.info("Browser closed.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
