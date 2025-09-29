from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service as FirefoxService
import os
import subprocess
import time
import sys
import signal
from db_connector import Database

web_app_process = None

def setup_test_database():
    """Initialize test database by running setup_test_db.py"""
    try:
        print("Setting up test database...")
        result = subprocess.run([sys.executable, "setup_test_db.py"],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("Test database setup completed successfully")
            print(result.stdout.strip())
            return True
        else:
            print(f"Database setup failed with return code {result.returncode}")
            print(f"Error: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print("Database setup timed out")
        return False
    except Exception as e:
        print(f"Error running database setup: {e}")
        return False

def get_test_config():
    """Get test configuration from database config table"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT api_gateway_url, browser_type, user_name FROM config WHERE id = 1")
        result = cursor.fetchone()
        if result:
            return {
                'api_gateway_url': result[0],
                'browser_type': result[1],
                'user_name': result[2]
            }
        else:
            print("No config found in database, using defaults")
            return {
                'api_gateway_url': '127.0.0.1:5001/users',
                'browser_type': 'Chrome',
                'user_name': 'test_user_123'
            }
    except Exception as e:
        print(f"Error getting config from database: {e}")
        return {
            'api_gateway_url': '127.0.0.1:5001/users',
            'browser_type': 'Chrome',
            'user_name': 'test_user_123'
        }
    finally:
        cursor.close()
        conn.close()

def create_driver(browser_type):
    """Create WebDriver based on browser type from config"""
    browser_type = browser_type.lower()

    if browser_type == 'firefox':
        service = FirefoxService(GeckoDriverManager().install())
        options = webdriver.FirefoxOptions()

        # Add headless mode for CI environments
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            options.add_argument('--headless')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        return webdriver.Firefox(service=service, options=options)
    else:  # Default to Chrome
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()

        # Add headless mode for CI environments
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            options.add_argument('--headless')

        # Chrome options for CI environments
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--window-size=1920,1080')

        # Unique user data directory to avoid conflicts
        import tempfile
        temp_dir = tempfile.mkdtemp()
        options.add_argument(f'--user-data-dir={temp_dir}')

        return webdriver.Chrome(service=service, options=options)

def start_web_app():
    """Start the web_app.py server as a background process"""
    global web_app_process
    try:
        print("Starting web_app.py server...")
        web_app_process = subprocess.Popen([sys.executable, "web_app.py"],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        # Give the server time to start
        time.sleep(3)
        print("Web app server started successfully")
        return True
    except Exception as e:
        print(f"Failed to start web app: {e}")
        return False

def stop_web_app():
    """Stop the web_app.py server"""
    global web_app_process
    if web_app_process:
        try:
            web_app_process.terminate()
            web_app_process.wait(timeout=5)
            print("Web app server stopped")
        except subprocess.TimeoutExpired:
            web_app_process.kill()
            print("Web app server forcefully killed")
        except Exception as e:
            print(f"Error stopping web app: {e}")

def test_user_interface(config):
    """
    Test the web interface for user data display
    1. Start a Selenium Webdriver session using config browser type
    2. Navigate to web interface URL using config URL and user
    3. Check that the user name element is showing (web element exists)
    4. Print user name (using locator)
    """

    # 1. Start a Selenium Webdriver session using config browser type
    print(f"Starting {config['browser_type']} browser...")
    driver = create_driver(config['browser_type'])

    try:
        # 2. Navigate to web interface URL using config URL and user
        # Parse the API gateway URL to extract host and port
        api_url = config['api_gateway_url']
        if api_url.startswith('http://'):
            base_url = api_url.replace('/users', '')
        else:
            base_url = f"http://{api_url.replace('/users', '')}"

        # Get user ID by querying the database for the configured user
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE user_name = %s", (config['user_name'],))
            result = cursor.fetchone()
            user_id = result[0] if result else "1"  # fallback to ID 1
        finally:
            cursor.close()
            conn.close()

        url = f"{base_url}/users/get_user_data/{user_id}"
        print(f"Navigating to: {url}")
        print(f"Testing with user: {config['user_name']} (ID: {user_id})")
        driver.get(url)

        # Wait for the page to load and check for elements
        wait = WebDriverWait(driver, 10)

        # 3. Check that the user name element is showing (web element exists)
        try:
            # Check for successful user display (H1 with id='user')
            user_element = wait.until(EC.presence_of_element_located((By.ID, "user")))
            print("User name element found!")

            # 4. Print user name (using locator)
            user_name = user_element.text
            print(f"User name: {user_name}")

        except:
            # Check if error element exists instead
            try:
                error_element = driver.find_element(By.ID, "error")
                print(f"Error found: {error_element.text}")
                raise Exception("test failed")
            except:
                print("Neither user nor error element found")
                raise Exception("test failed")

    except Exception as e:
        print(f"Test failed with error: {e}")
        raise Exception("test failed")

    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    # Initialize test database first
    if not setup_test_database():
        print("Cannot proceed with testing - database setup failed")
        sys.exit(1)

    # Get test configuration from database
    print("Loading test configuration from database...")
    config = get_test_config()
    print(f"Config loaded: URL={config['api_gateway_url']}, Browser={config['browser_type']}, User={config['user_name']}")

    # Start the web app server
    if not start_web_app():
        print("Cannot proceed with testing - web app failed to start")
        sys.exit(1)

    try:
        # Run tests with database configuration
        test_user_interface(config)
    finally:
        # Always stop the web app server when done
        stop_web_app()