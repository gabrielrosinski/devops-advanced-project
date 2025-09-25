from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = FastAPI()

@app.get("/simple-scrape")
async def simple_scrape(url: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        title = driver.title
        
        return {"title": title, "url": url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if driver:
            driver.quit()