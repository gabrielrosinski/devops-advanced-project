from db_connector import Database
import requests
import json

url = "http://127.0.0.1:5000/users"

headers = {
    "Content-Type": "application/json"
}

def clear_users_data():
    """Clear all data from the users table without dropping it"""
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
    """Get specific user by ID"""
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
    """Verify user exists in database"""
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
            