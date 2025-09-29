"""
Web Interface Application

FastAPI-based web application that provides HTML responses for user data visualization.
Serves as a web frontend for displaying user information retrieved from the database.

Endpoints:
    GET /users/get_user_data/{user_id} - Display user information as HTML

Dependencies:
    - FastAPI: Web framework
    - Database: Custom database connector
    - uvicorn: ASGI server

Environment Variables:
    HOST: Server host address (default: 127.0.0.1)
    WEB_PORT: Server port (default: 5001)

Usage:
    python web_app.py
"""

import os
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from db_connector import Database
from server_utiliy import shutdown_server
from fastapi import HTTPException

load_dotenv()

app = FastAPI()                                                                                                                                                                                                     
db = Database() 

def get_user_name_from_db(user_id):
    """Retrieve username from database by user ID.

    Args:
        user_id (str): ID of the user to look up

    Returns:
        str or None: Username if found, None if not found
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
         cursor.execute("SELECT user_name FROM users WHERE id = %s", (user_id,))
         result = cursor.fetchone()
         return result[0] if result else None
    finally:
        cursor.close()
        conn.close()
        
@app.get('/healthz')
async def health_check():
    """Health check endpoint for monitoring service status."""
    return {"status": "healthy", "service": "web-app"}

@app.get('/stop_server')
async def stop_server():
    """Gracefully stop the web server with error handling."""
    try:
        print("Shutdown request received")
        response = {"message" : "Server shutting down gracefully"}
        asyncio.create_task(shutdown_server())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to stop the server: {str(e)}")    
        

@app.get("/users/get_user_data/{user_id}", response_class=HTMLResponse)
def get_user_data(user_id: str):
    """Display user data as HTML page.

    Args:
        user_id (str): ID of the user to display

    Returns:
        str: HTML response with user name or error message

    Example:
        GET /users/get_user_data/1
        Returns: <H1 id='user'>John Doe</H1>
    """
    user_name = get_user_name_from_db(user_id)
    if user_name is None:
        return f"<H1 id='error'>no such user: {user_id}</H1>"
    
    return f"<H1 id='user'>{user_name}</H1>"
    
if __name__ == "__main__":
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("WEB_PORT", 5001))
    uvicorn.run("web_app:app", host=HOST, port=PORT, reload=True)