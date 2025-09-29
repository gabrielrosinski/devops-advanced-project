import os
from dotenv import load_dotenv
from db_connector import Database

load_dotenv()

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

try:
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS config")
    cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("INSERT INTO users (user_name) VALUES (%s)", ('test_user_123',))
    
    cursor.execute("""
        CREATE TABLE config (
            id INT AUTO_INCREMENT PRIMARY KEY,
            api_gateway_url VARCHAR(255) NOT NULL,
            browser_type VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL
        )
    """)
    cursor.execute("INSERT INTO config (api_gateway_url, browser_type, user_name) VALUES (%s, %s, %s)", ('127.0.0.1:5001/users', 'Chrome', 'test_user_123'))
    
    conn.commit()
    print("Test database setup complete - User ID 1 created")
finally:
    cursor.close()
    conn.close()