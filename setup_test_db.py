import os
from dotenv import load_dotenv
from db_connector import Database

load_dotenv()

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

try:
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("INSERT INTO users (user_name) VALUES ('Test User')")
    conn.commit()
    print("Test database setup complete - User ID 1 created")
finally:
    cursor.close()
    conn.close()