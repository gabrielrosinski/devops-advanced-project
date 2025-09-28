"""
Combined Testing Module

This module provides end-to-end testing for a FastAPI REST API and web interface.
It performs complete user lifecycle testing from API creation to web verification.

Test Flow:
    1. POST new user data to REST API
    2. GET user data to verify it matches posted data
    3. Verify user exists in database using direct SQL query
    4. Start Selenium WebDriver session
    5. Navigate to web interface using user ID
    6. Verify username is correctly displayed on web page

Dependencies:
    - requests: HTTP client for API testing
    - selenium: Web browser automation
    - webdriver_manager: Automatic WebDriver management
    - Database: Custom database connector

Configuration:
    REST API: http://127.0.0.1:5000/users
    Web Interface: http://127.0.0.1:5001/users/get_user_data

Usage:
    python combined_testing.py
"""

from db_connector import Database
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import sys
import time

# Configuration
REST_URL = "http://127.0.0.1:5000/users"
WEB_URL = "http://127.0.0.1:5001/users/get_user_data"
HEADERS = {"Content-Type": "application/json"}

# Global process variables
rest_app_process = None
web_app_process = None

def start_apps():
    """Start both rest_app and web_app servers"""
    global rest_app_process, web_app_process
    rest_app_process = subprocess.Popen([sys.executable, "rest_app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    web_app_process = subprocess.Popen([sys.executable, "web_app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)  # Wait for both servers to start

def stop_apps():
    """Stop both servers"""
    if rest_app_process: rest_app_process.terminate()
    if web_app_process: web_app_process.terminate()

def clear_users_data():
    """Clear all user data from the database.

    Connects to the database and deletes all records from the users table
    without dropping the table structure.

    Raises:
        Exception: If database connection or query fails
    """
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users")
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def post_new_user(user_name):
    """Create a new user via REST API POST request.

    Args:
        user_name (str): The name of the user to create

    Returns:
        tuple: A tuple containing (user_id, user_name)

    Raises:
        AssertionError: If API response is invalid or status code != 200

    Example:
        >>> user_id, name = post_new_user("John Doe")
        >>> print(f"Created user {name} with ID {user_id}")
    """
    print(f"1. POST user '{user_name}'")

    response = requests.post(REST_URL, json={"user_name": user_name}, headers=HEADERS)
    data = response.json()

    assert response.status_code == 200, f"POST failed: {response.status_code}"
    assert "user_id" in data, "Missing user_id"
    assert data["user_name"] == user_name, "Username mismatch"

    return data["user_id"], user_name

def get_user_by_id(user_id):
    """Retrieve user data by ID via REST API GET request.

    Args:
        user_id (int): The ID of the user to retrieve

    Returns:
        tuple: Database record tuple (id, name, created_at, updated_at)

    Raises:
        AssertionError: If API response is invalid or user not found

    Example:
        >>> user_data = get_user_by_id(1)
        >>> print(f"User: {user_data[1]}")
    """
    print(f"2. GET user {user_id}")

    response = requests.get(f"{REST_URL}/{user_id}", headers=HEADERS)
    data = response.json()

    assert response.status_code == 200, f"GET failed: {response.status_code}"
    assert "user" in data, "Missing user key"

    return data["user"]

def verify_user_in_database(user_name):
    """Verify user exists in database using direct database query.

    Args:
        user_name (str): The username to search for in the database

    Returns:
        tuple: Database record if found

    Raises:
        AssertionError: If user not found in database

    Example:
        >>> record = verify_user_in_database("John Doe")
        >>> print(f"Found user: {record}")
    """
    print(f"3. Verify '{user_name}' in DB")

    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (user_name,))
        result = cursor.fetchone()
        assert result and result[1] == user_name, f"User '{user_name}' not found in DB"
        return result
    finally:
        cursor.close()
        conn.close()

def start_selenium_session():
    """Initialize and configure Chrome WebDriver for automated testing.

    Configures Chrome with headless mode and other CI-friendly options.
    Automatically manages ChromeDriver installation.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance

    Raises:
        Exception: If WebDriver initialization fails

    Example:
        >>> driver = start_selenium_session()
        >>> driver.get("https://example.com")
    """
    print("4. Start WebDriver")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def navigate_to_web_interface(driver, user_id):
    """Navigate to the web interface for a specific user.

    Args:
        driver: Selenium WebDriver instance
        user_id (int): ID of the user to view in web interface

    Raises:
        TimeoutException: If page doesn't load within 10 seconds

    Example:
        >>> navigate_to_web_interface(driver, 1)
    """
    print(f"5. Navigate to web interface for user {user_id}")

    driver.get(f"{WEB_URL}/{user_id}")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

def verify_user_name_on_web(driver, expected_name):
    """Verify the displayed username matches expected value on web page.

    Locates the H1 element with id='user' and compares its text content
    with the expected username.

    Args:
        driver: Selenium WebDriver instance
        expected_name (str): The expected username to verify

    Raises:
        AssertionError: If displayed name doesn't match expected name
        TimeoutException: If user element not found within 10 seconds

    Example:
        >>> verify_user_name_on_web(driver, "John Doe")
    """
    print(f"6. Verify '{expected_name}' on web")

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user")))
    displayed_name = element.text

    assert displayed_name == expected_name, f"Expected '{expected_name}', got '{displayed_name}'"

def combined_test():
    """Execute the complete 6-step end-to-end test suite.

    Performs the following test sequence:
    1. POST new user to REST API
    2. GET user data to verify it matches posted data
    3. Verify user exists in database using direct SQL query
    4. Start Selenium WebDriver session
    5. Navigate to web interface using user ID
    6. Verify username is correctly displayed on web page

    Returns:
        bool: True if all tests pass, False otherwise

    Example:
        >>> success = combined_test()
        >>> print("All tests passed!" if success else "Tests failed!")
    """
    print("=== COMBINED TEST START ===")

    start_apps()
    clear_users_data()
    test_user_name = "Combined Test User"
    driver = None

    try:
        # Steps 1-6
        user_id, user_name = post_new_user(test_user_name)
        user_data = get_user_by_id(user_id)

        # Verify GET data matches POST data
        assert user_data[1] == user_name, f"Data mismatch: POST='{user_name}', GET='{user_data[1]}'"
        print("✓ GET data matches POST data")

        verify_user_in_database(user_name)
        driver = start_selenium_session()
        navigate_to_web_interface(driver, user_id)
        verify_user_name_on_web(driver, user_name)

        print("🎉 ALL TESTS PASSED!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise Exception("test failed")
    finally:
        if driver:
            driver.quit()
        stop_apps()

if __name__ == "__main__":
    combined_test()