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

url = "http://127.0.0.1:5000/users"

headers = {
    "Content-Type": "application/json"
}

def clear_users_data():
    """Clear all data from the users table without dropping it.

    Connects to the database and executes a DELETE statement to remove
    all records from the users table while preserving the table structure.

    Raises:
        Exception: If database operation fails
    """
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM users")
        conn.commit()
        print("All user data cleared from users table")
    except Exception as e:
        print(f"Error clearing users data: {e}")
    finally:
        cursor.close()
        conn.close()
        
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
        return None
    except Exception as e:
        print(f"Error making POST request: {e}")
        return None


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
        return None
    except Exception as e:
        print(f"Error making GET request: {e}")
        return None

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
        return None
    except Exception as e:
        print(f"Error making GET request: {e}")
        return None

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
        return False
    finally:
        cursor.close()
        conn.close()

                
        
if __name__ == "__main__":
    print("=== BACKEND TESTING START ===")

    # Step 1: Clear existing data
    print("\n1. Clearing existing data...")
    clear_users_data()

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
            