from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os


def test_user_interface(user_id):
    """
    Test the web interface for user data display
    1. Start a Selenium Webdriver session
    2. Navigate to web interface URL using an existing user id
    3. Check that the user name element is showing (web element exists)
    4. Print user name (using locator)
    """

    # 1. Start a Selenium Webdriver session
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # Get the web app URL from environment or use default
        host = os.getenv("HOST", "127.0.0.1")
        port = os.getenv("WEB_PORT", "5001")
        base_url = f"http://{host}:{port}"

        # 2. Navigate to web interface URL using an existing user id
        url = f"{base_url}/users/get_user_data/{user_id}"
        print(f"Navigating to: {url}")
        driver.get(url)

        # Wait for the page to load and check for elements
        wait = WebDriverWait(driver, 10)

        # 3. Check that the user name element is showing (web element exists)
        try:
            # Check for successful user display (H1 with id='user')
            user_element = wait.until(EC.presence_of_element_located((By.ID, "user")))
            print("User name element found!")

            # 4. Print user name (using locator)
            user_name = user_element.text
            print(f"User name: {user_name}")

        except:
            # Check if error element exists instead
            try:
                error_element = driver.find_element(By.ID, "error")
                print(f"Error found: {error_element.text}")
            except:
                print("Neither user nor error element found")

    except Exception as e:
        print(f"Test failed with error: {e}")

    finally:
        # Close the browser
        driver.quit()


# if __name__ == "__main__":
#     # Test with a sample user ID
#     test_user_id = input("Enter user ID to test (or press Enter for default '1'): ").strip()
#     if not test_user_id:
#         test_user_id = "1"

#     test_user_interface(test_user_id)

if __name__ == "__main__":
    # Use environment variable or default for automation
    test_user_id = os.getenv("TEST_USER_ID", "1")
    test_user_interface(test_user_id)