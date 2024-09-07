import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Specify the path to ChromeDriver
chrome_driver_path = "D:/S9/miniproject/edit 2/chromedriver-win64/chromedriver.exe"  # Update with the actual path

# Set up the WebDriver (e.g., Chrome)
try:
    driver = webdriver.Chrome(executable_path=chrome_driver_path)  # Ensure chromedriver is in PATH or specify executable_path
    logger.info("WebDriver initialized successfully.")

    # Open the login page
    driver.get("http://localhost:8000/login")  # Update with your actual URL
    logger.info("Opened login page.")

    # Wait for the page to load
    time.sleep(2)

    # Function to test login with credentials
    def login_test(username, password, expected_result):
        # Find the username and password fields and the submit button
        username_field = driver.find_element(By.NAME, "username")  # Update with actual field name
        password_field = driver.find_element(By.NAME, "password")  # Update with actual field name
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        # Input credentials
        username_field.clear()
        password_field.clear()
        username_field.send_keys(username)
        password_field.send_keys(password)
        logger.info(f"Testing login with username: {username} and password: {password}")

        # Submit the form
        submit_button.click()
        time.sleep(2)

        # Check for success or failure based on expected result
        if expected_result == "fail":
            try:
                error_message = driver.find_element(By.CLASS_NAME, "error-message")  # Update with actual error class or element
                if error_message:
                    logger.info("Login failed as expected.")
                else:
                    logger.error("Login did not fail as expected.")
            except:
                logger.error("Login did not fail as expected.")
        elif expected_result == "success":
            try:
                # Check if the URL has changed to the expected successful page
                if "lessor_index" in driver.current_url:  # Adjust this based on your post-login page
                    logger.info("Login succeeded as expected.")
                else:
                    logger.error(f"Login did not succeed. Current URL: {driver.current_url}")
            except Exception as e:
                logger.error(f"An error occurred during success check: {e}")

    # Test 1: Wrong credentials
    login_test("wrong_user", "wrong_password", "fail")

    # Test 2: Correct credentials
    login_test("jhon@gmail.com", "gDSN:,pb,4u45F2", "success")

except Exception as e:
    logger.error(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
    logger.info("Browser closed.")
