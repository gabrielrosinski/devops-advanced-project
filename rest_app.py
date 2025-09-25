"""
REST API Application

FastAPI-based REST API for user management with CRUD operations.
Provides endpoints for creating, reading, updating, and deleting user records.

Endpoints:
    POST /users - Create a new user
    GET /users - Retrieve all users
    GET /users/{user_id} - Retrieve specific user by ID
    PUT /users/{user_id} - Update user information
    DELETE /users/{user_id} - Delete user by ID

Dependencies:
    - FastAPI: Web framework
    - Pydantic: Data validation
    - uvicorn: ASGI server
    - Database: Custom database connector

Environment Variables:
    HOST: Server host address (default: 0.0.0.0)
    PORT: Server port (default: 5000)
    RELOAD: Enable auto-reload in development (default: true)

Usage:
    python rest_app.py
"""

import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
from db_connector import Database
from typing import Optional
from datetime import datetime

load_dotenv()

db = Database()

def get_db():
    """Database dependency for FastAPI dependency injection.

    Yields:
        pymysql.Connection: Database connection that auto-closes after request
    """
    connection = db.get_connection()
    try:
        yield connection
    finally:
        connection.close()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"

app = FastAPI()

class User(BaseModel):
    """User data model for request/response validation.

    Attributes:
        user_name (str): Name of the user
        created_at (Optional[datetime]): Timestamp when user was created
        updated_at (Optional[datetime]): Timestamp when user was last updated
    """
    user_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@app.post("/users")
async def create_user(user: User, conn = Depends(get_db)):
    """Create a new user.

    Args:
        user (User): User data from request body
        conn: Database connection from dependency injection

    Returns:
        dict: Success message with user_id and user_name

    Example:
        POST /users
        {"user_name": "John Doe"}
    """
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (user_name, created_at) VALUES (%s, NOW())", (user.user_name,))
        conn.commit()
        user_id = cursor.lastrowid
        return {"message": "User created successfully", "user_id": user_id, "user_name": user.user_name}
    finally:
        cursor.close()

@app.get("/users")
async def get_all_users(conn = Depends(get_db)):
    """Retrieve all users from the database.

    Args:
        conn: Database connection from dependency injection

    Returns:
        dict: Dictionary containing list of all users

    Example:
        GET /users
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return {"users": users}
    finally:
        cursor.close()

@app.get("/users/{user_id}")
async def get_user(user_id: int, conn = Depends(get_db)):
    """Retrieve a specific user by ID.

    Args:
        user_id (int): ID of the user to retrieve
        conn: Database connection from dependency injection

    Returns:
        dict: User data or error message if not found

    Example:
        GET /users/1
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user is None:
            return {"error": "User not found"}
        return {"user": user}
    finally:
        cursor.close()

@app.put("/users/{user_id}")
async def update_user_name(user_id: int, user: User, conn = Depends(get_db)):
    """Update user information.

    Args:
        user_id (int): ID of the user to update
        user (User): Updated user data from request body
        conn: Database connection from dependency injection

    Returns:
        dict: Success message or error if user not found

    Example:
        PUT /users/1
        {"user_name": "Jane Doe"}
    """
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET user_name = %s, updated_at = NOW() WHERE id = %s", (user.user_name, user_id))
        conn.commit()
        if cursor.rowcount == 0:
            return {"error": "User not found"}
        return {"message": "User updated successfully", "user_id": user_id, "user_name": user.user_name}
    finally:
        cursor.close()

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, conn = Depends(get_db)):
    """Delete a user by ID.

    Args:
        user_id (int): ID of the user to delete
        conn: Database connection from dependency injection

    Returns:
        dict: Success message or error if user not found

    Example:
        DELETE /users/1
    """
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id))
        conn.commit()
        if cursor.rowcount == 0:
            return {"error": "User not found"}
        return {"message": f"User with id {user_id} was deleted successfully"}
    finally:
        cursor.close()

if __name__ == "__main__":
    uvicorn.run(
        "rest_app:app",  # file_name:fastapi_instance
        host=HOST,
        port=PORT,
        reload=RELOAD
    )
    
    
    
# > where we need to have the .env vars while using github action. in github secret ?

# ● Yes, for GitHub Actions you should store environment variables as GitHub Secrets. Here's how:

#   GitHub Secrets Setup

#   1. Repository Settings → Secrets and variables → Actions
#   2. Add repository secrets for each environment variable:
#     - HOST
#     - WEB_PORT
#     - PORT
#     - DB_HOST
#     - DB_USER
#     - DB_PASSWORD
#     - Any other .env variables

#   GitHub Actions Workflow

#   In your .github/workflows/*.yml file:

#   jobs:
#     test:
#       runs-on: ubuntu-latest
#       env:
#         HOST: ${{ secrets.HOST }}
#         WEB_PORT: ${{ secrets.WEB_PORT }}
#         PORT: ${{ secrets.PORT }}
#         DB_HOST: ${{ secrets.DB_HOST }}
#         DB_USER: ${{ secrets.DB_USER }}
#         DB_PASSWORD: ${{ secrets.DB_PASSWORD }}

#       steps:
#         - uses: actions/checkout@v4
#         - name: Run tests
#           run: poetry run python test/frontend_testing.py

#   Never commit .env files to the repository - GitHub Secrets keep sensitive data secure in CI/CD pipelines.   