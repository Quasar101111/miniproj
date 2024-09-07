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

    # Test 1: "second"
    def run_test_second():
        logger.info("Running test: second")

        # Open the login page
        driver.get("http://127.0.0.1:8000/login/")
        logger.info("Opened login page.")

        # Set window size
        driver.set_window_size(945, 913)
        logger.info("Set window size to 945x913")

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

        # # Navigate to "LEASES" from the navbar
        # leases_nav = driver.find_element(By.ID, "navbarDropdownMenuLink")
        # leases_nav.click()
        # logger.info("Clicked 'LEASES' in navbar.")

        # # Click on "Rented Warehouses"
        # rented_warehouses = driver.find_element(By.LINK_TEXT, "Rented Warehouses")
        # rented_warehouses.click()
        # logger.info("Navigated to 'Rented Warehouses'.")

        # # Download a report
        # download_report = driver.find_element(By.LINK_TEXT, "Download Report")
        # download_report.click()
        # logger.info("Clicked on 'Download Report'.")
        # time.sleep(2)

    # Test 2: "third"
    def run_test_third():
        logger.info("Running test: third")

        # Open the home page
        driver.get("http://127.0.0.1:8000/")
        logger.info("Opened home page.")

        # Set window size
        driver.set_window_size(1936, 1048)
        logger.info("Set window size to 1936x1048")

        # Click on the first card (warehouse selection)
        first_card = driver.find_element(By.CSS_SELECTOR, ".col-md-4:nth-child(1) .card-body")
        first_card.click()
        logger.info("Clicked on the first card.")

        # Click the 'Start Chat' button
        start_chat_button = driver.find_element(By.CSS_SELECTOR, ".btn-block")
        start_chat_button.click()
        logger.info("Clicked 'Start Chat' button.")
        time.sleep(2)

    # Running the tests
    run_test_second()
    run_test_third()

except Exception as e:
    logger.error(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
    logger.info("Browser closed.")



