import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Specify the path to ChromeDriver
chrome_driver_path = "D:/S9/miniproject/edit 2/chromedriver-win64/chromedriver.exe"  # Update with the actual path

# Initialize driver variable
driver = None

try:
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--start-maximized')

    # Initialize the WebDriver with the correct syntax
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    logger.info("WebDriver initialized successfully.")

    # Test 1: "second"
    def run_test_second():
        logger.info("Running test: second")

        # Open the login page
        driver.get("http://127.0.0.1:8000/login/")
        logger.info("Opened login page.")

        # Set window size
        driver.set_window_size(1024, 720)
        logger.info("Set window size to 1024x720")

        # Find and click the username field
        username_field = driver.find_element(By.ID, "id_username")
        username_field.click()
        logger.info("Clicked on username field.")

        # Input username
        username_field.send_keys("agustine@gmail.com")
        logger.info("Entered username: agustine@gmail.com")

        # Find and click the password field
        password_field = driver.find_element(By.ID, "id_password")
        password_field.click()
        logger.info("Clicked on password field.")

        # Input password
        password_field.send_keys("gDSN:,pb,4u45F2")
        logger.info("Entered password.")

        # Click the submit button
        submit_button = driver.find_element(By.CSS_SELECTOR, ".btn")
        submit_button.click()
        logger.info("Clicked the submit button.")
        time.sleep(2)

    # Test 2: "third"
    def run_test_third():
        logger.info("Running test: third")

        # Open the home page
        driver.get("http://127.0.0.1:8000/")
        logger.info("Opened home page.")
        time.sleep(2)
        # Set window size
        driver.set_window_size(1024, 720)
        logger.info("Set window size to 1024x720")

        # Click on the first card (warehouse selection)
        first_card = driver.find_element(By.CSS_SELECTOR, ".col-md-4:nth-child(1) .card-body")
        first_card.click()
        logger.info("Clicked on the first card.")
        time.sleep(2)

        # Click the 'Start Chat' button
        start_chat_button = driver.find_element(By.CSS_SELECTOR, ".btn-block")
        start_chat_button.click()
        time.sleep(2)
        logger.info("Clicked 'Start Chat' button.")
        time.sleep(2)

    # Running the tests
    run_test_second()
    run_test_third()

except Exception as e:
    logger.error(f"An error occurred: {e}")

finally:
    # Close the browser if it was initialized
    if driver:
        driver.quit()
        logger.info("Browser closed.")



