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
    driver.get("http://127.0.0.1:8000/login/")  # Base URL + /login/
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

    # Wait for login to complete
    time.sleep(2)

    # Navigate to "LEASES" from the navbar
    leases_nav = driver.find_element(By.ID, "navbarDropdownMenuLink")
    leases_nav.click()
    logger.info("Clicked 'LEASES' in navbar.")

    # Click on "Rented Warehouses"
    rented_warehouses = driver.find_element(By.LINK_TEXT, "Rented Warehouses")
    rented_warehouses.click()
    logger.info("Navigated to 'Rented Warehouses'.")

    # Download a report
    download_report = driver.find_element(By.LINK_TEXT, "Download Report")
    download_report.click()
    logger.info("Clicked on 'Download Report'.")

    # Wait for actions to complete
    time.sleep(2)

except Exception as e:
    logger.error(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
    logger.info("Browser closed.")