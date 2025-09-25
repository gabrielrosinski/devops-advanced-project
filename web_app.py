import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from db_connector import Database
import uvicorn                                                                                                                                                                                           
                                                                                                                                                                                                                            
load_dotenv()                                                                                                                                                                                                               
                                                                                                                                                                                                                           
app = FastAPI()                                                                                                                                                                                                     
db = Database() 

def get_user_name_from_db(user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
         cursor.execute("SELECT user_name FROM users WHERE id = %s", (user_id,))
         result = cursor.fetchone()
         return result[0] if result else None
    finally:
        cursor.close()
        conn.close()

@app.get("/users/get_user_data/{user_id}", response_class=HTMLResponse)
def get_user_data(user_id: str):
    user_name = get_user_name_from_db(user_id)
    if user_name is None:
        return f"<H1 id='error'>no such user: {user_id}</H1>"
    
    return f"<H1 id='user'>{user_name}</H1>"
    
if __name__ == "__main__":
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("WEB_PORT", 5001))
    uvicorn.run("web_app:app", host=HOST, port=PORT, reload=True)