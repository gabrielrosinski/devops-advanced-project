"""
Backend Testing Module

This module provides comprehensive testing for the REST API backend.
It includes tests for user creation, retrieval, and database verification.

Test Functions:
    - clear_users_data(): Clear all user data from database
    - test_create_user(): Test POST user creation endpoint
    - test_get_new_user(): Test GET all users endpoint
    - test_get_user_by_id(): Test GET specific user endpoint
    - verify_user_in_db(): Verify user exists in database

Configuration:
    REST API URL: http://127.0.0.1:5000/users

Usage:
    python backend_testing.py
"""

from db_connector import Database
import requests
import subprocess
import sys
import time

url = "http://127.0.0.1:5000/users"

headers = {
    "Content-Type": "application/json"
}

web_app_process = None

def check_mysql_docker():
    """Check if MySQL Docker container is running"""
    try:
        print("Checking MySQL Docker container status...")
        result = subprocess.run(['docker', 'ps', '--filter', 'name=mysql', '--format', 'table {{.Names}}\t{{.Status}}'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            print("Error running docker command")
            return False

        output = result.stdout.strip()
        lines = output.split('\n')

        if len(lines) < 2:  # Only header line, no containers
            print("No MySQL container found")
            return False

        # Check if any line contains "Up" status
        for line in lines[1:]:  # Skip header
            if 'Up' in line:
                print("MySQL Docker container is running")
                return True

        print("MySQL Docker container is not running")
        return False

    except subprocess.TimeoutExpired:
        print("Docker command timed out")
        return False
    except FileNotFoundError:
        print("Docker command not found - is Docker installed?")
        return False
    except Exception as e:
        print(f"Error checking MySQL Docker: {e}")
        return False

def test_create_user():
    """Test user creation via POST request to REST API.

    Creates a test user and validates the API response contains
    the expected fields and values.

    Returns:
        requests.Response or None: API response if successful, None if failed

    Raises:
        AssertionError: If API response validation fails
    """
    user_data = {
        "user_name": "Test User"
    }

    try:
        response = requests.post(url, json=user_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        response_data = response.json()
        assert "user_id" in response_data, "Response missing user_id"
        assert response_data["user_name"] == user_data["user_name"], "Username mismatch"
        assert "message" in response_data, "Response missing message"

        return response
    except AssertionError as e:
        print(f"Assertion failed: {e}")
        raise Exception("test failed")
    except Exception as e:
        print(f"Error making POST request: {e}")
        raise Exception("test failed")


def test_get_new_user():
    """Test retrieval of all users via GET request.

    Makes a GET request to retrieve all users and validates
    the response structure.

    Returns:
        requests.Response or None: API response if successful, None if failed

    Raises:
        AssertionError: If API response validation fails
    """
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        response_data = response.json()
        assert "users" in response_data, "Response missing users key"
        assert isinstance(response_data["users"], list), "Users should be a list"

        return response
    except AssertionError as e:
        print(f"Assertion failed: {e}")
        raise Exception("test failed")
    except Exception as e:
        print(f"Error making GET request: {e}")
        raise Exception("test failed")

def test_get_user_by_id(user_id):
    """Test retrieval of specific user by ID.

    Args:
        user_id (int): ID of the user to retrieve

    Returns:
        requests.Response or None: API response if successful, None if failed

    Raises:
        AssertionError: If API response validation fails
    """
    get_url = f"http://127.0.0.1:5000/users/{user_id}"

    try:
        response = requests.get(get_url, headers=headers)
        print(f"GET User ID {user_id} - Status Code: {response.status_code}")
        print(f"GET Response: {response.json()}")

        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        response_data = response.json()
        assert "user" in response_data, "Response missing user key"

        return response
    except AssertionError as e:
        print(f"GET assertion failed: {e}")
        raise Exception("test failed")
    except Exception as e:
        print(f"Error making GET request: {e}")
        raise Exception("test failed")

def verify_user_in_db(user_name):
    """Verify user exists in database using direct SQL query.

    Args:
        user_name (str): Username to search for in database

    Returns:
        bool: True if user found and verified, False otherwise

    Raises:
        AssertionError: If user not found or data doesn't match
    """
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (user_name,))
        result = cursor.fetchone()

        # Assertions
        assert result is not None, f"User '{user_name}' not found in database"
        assert result[1] == user_name, f"Expected {user_name}, got {result[1]}"

        print(f"DB Record verified: {result}")
        return True
    except AssertionError as e:
        print(f"Database assertion failed: {e}")
        raise Exception("test failed")
    finally:
        cursor.close()
        conn.close()

def start_rest_app():
    """Start the web_app.py server as a background process"""
    global web_app_process
    try:
        print("Starting rest_app.py server...")
        web_app_process = subprocess.Popen([sys.executable, "rest_app.py"],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        # Give the server time to start
        time.sleep(3)
        print("Rest app server started successfully")
        return True
    except Exception as e:
        print(f"Failed to start rest app: {e}")
        return False
                
        
if __name__ == "__main__":
    print("=== BACKEND TESTING START ===")

    # Check MySQL Docker container first
    print("\n0. Checking MySQL Docker container...")
    if not check_mysql_docker():
        print("Cannot proceed with testing - MySQL Docker container is not running")
        print("Please start MySQL Docker container and try again")
        exit(1)

    db = Database()

    # Step 1: Clear existing data
    print("\n1. Clearing existing data...")
    Database.clear_data()
    
    # Start the web app server
    if not start_rest_app():
        print("Cannot proceed with testing - rest app failed to start")
        sys.exit(1)

    # Step 2: Test POST - Create new user
    print("\n2. Testing POST - Create new user...")
    post_response = test_create_user()

    if post_response:
        # Extract user_id from POST response for next tests
        user_id = post_response.json().get("user_id")
        user_name = post_response.json().get("user_name")

        # Step 3: Test GET by ID - Verify posted data
        print(f"\n3. Testing GET by ID - Verify user {user_id}...")
        test_get_user_by_id(user_id)

        # Step 4: Test GET all users
        print("\n4. Testing GET all users...")
        test_get_new_user()

        # Step 5: Verify data in database
        print(f"\n5. Verifying user '{user_name}' in database...")
        verify_user_in_db(user_name)

    print("\n=== BACKEND TESTING COMPLETE ===")
            