# FastAPI User Management Application Suite

A comprehensive FastAPI-based application suite with REST API, web interface, database management, and automated testing capabilities.

## Project Overview

This project consists of multiple interconnected applications:

- **REST API Server** (`rest_app.py`) - Full CRUD operations for user management
- **Web Interface** (`web_app.py`) - HTML frontend for displaying user data
- **Database Layer** (`db_connector.py`) - MySQL connection and operations
- **Testing Suite** - Comprehensive backend, frontend, and end-to-end testing
- **Configuration Management** - Database-driven test configuration

## Project Structure

```
├── rest_app.py           # REST API server (port 5000)
├── web_app.py            # Web interface server (port 5001)
├── db_connector.py       # Database connection and operations
├── server_utiliy.py      # Server shutdown utility
├── clean_environment.py  # Environment cleanup script
├── setup_test_db.py      # Database initialization and test data
├── backend_testing.py    # REST API testing
├── frontend_testing.py   # Web interface testing (Selenium)
├── combined_testing.py   # End-to-end testing
├── requirements.txt      # Python dependencies
├── .env                  # Environment configuration
├── CLAUDE.md            # Development guidance
└── README.md            # This file
```

## Requirements

### System Requirements
- **Python 3.9+**
- **Docker** (for MySQL container)
- **Docker Compose** (optional, recommended)

### Browser Requirements (for testing)
- **Chrome** or **Firefox** (automatically managed by WebDriver)

## Environment Configuration

### 1. Create .env File

Create a `.env` file in the project root with the following configuration:

```bash
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=black
DB_NAME=users_db
DB_ROOT_USER=root
DB_ROOT_PASSWORD=black

# REST API Configuration
HOST=0.0.0.0
PORT=5000
RELOAD=true

# Web Interface Configuration
WEB_PORT=5001

# Testing Configuration
Test User=1
```

**Important:** Ensure the database passwords match your MySQL container configuration.

## Dependency Installation

### Option A: Using pip (Current Setup)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## MySQL Database Setup

### 1. Install Docker

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

**On macOS:**
```bash
brew install --cask docker
# Start Docker Desktop from Applications
```

**On Windows:**
Download and install Docker Desktop from [official website](https://www.docker.com/products/docker-desktop/)

### 2. Start MySQL Container

**Option A: Using Docker Command**
```bash
docker run -d \
  --name mysql-container \
  -e MYSQL_ROOT_PASSWORD=black \
  -e MYSQL_DATABASE=users_db \
  -p 3306:3306 \
  mysql:8.0
```

**Option B: Using Docker Compose (if available)**
```bash
docker-compose up -d mysql
```

### 3. Verify MySQL Container
```bash
# Check if container is running
docker ps | grep mysql

# Check MySQL logs
docker logs mysql-container

# Connect to MySQL (optional)
docker exec -it mysql-container mysql -u root -p
```

## Database Initialization

### setup_test_db.py

This script initializes the database with the required tables and test data:

```bash
# Ensure MySQL container is running first
python setup_test_db.py
```

**What it does:**
- Drops existing tables if they exist
- Creates fresh `users` and `config` tables
- Inserts default test data
- Prepares database for testing

### Database Schema

The application uses two main tables:

#### users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### config Table
```sql
CREATE TABLE config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_gateway_url VARCHAR(255) NOT NULL,
    browser_type VARCHAR(50) NOT NULL,
    user_name VARCHAR(100) NOT NULL
);
```

**Default config data:**
- `api_gateway_url`: `127.0.0.1:5001/users`
- `browser_type`: `Chrome`
- `user_name`: `test_user_123`

## Running the Applications

### 1. REST API Server (rest_app.py)

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start REST API server
python rest_app.py
```

**Features:**
- Runs on `http://0.0.0.0:5000` (configurable via HOST/PORT env vars)
- Auto-reload enabled in development
- Swagger documentation at `http://localhost:5000/docs`
- ReDoc documentation at `http://localhost:5000/redoc`

### 2. Web Interface Server (web_app.py)

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Start web interface server
python web_app.py
```

**Features:**
- Runs on `http://127.0.0.1:5001` (configurable via WEB_PORT env var)
- Serves HTML responses for user data visualization
- Integrates with REST API for data retrieval

### 3. Manual Server Management

Both servers need to be running for full functionality:

```bash
# Terminal 1: Start REST API
python rest_app.py

# Terminal 2: Start Web Interface
python web_app.py
```

## Application Descriptions

### rest_app.py - REST API Server
- **Purpose**: Provides RESTful API endpoints for user management
- **Port**: 5000 (configurable)
- **Features**: Full CRUD operations, data validation, automatic database connection, health checks, graceful shutdown
- **Security**: SQL injection protection via prepared statements, custom 404 error handling

### web_app.py - Web Interface
- **Purpose**: HTML frontend for displaying user data
- **Port**: 5001 (configurable)
- **Features**: User data visualization, error handling for missing users, health checks, graceful shutdown
- **Integration**: Queries database directly for user information
- **Security**: Custom 404 error handling

### db_connector.py - Database Layer
- **Purpose**: Centralized database connection and operations
- **Features**: Connection pooling, automatic database/table creation, prepared statements
- **Methods**: `get_connection()`, `clear_data()`, database initialization

### server_utiliy.py - Server Shutdown Utility
- **Purpose**: Provides graceful server shutdown functionality
- **Features**: Async shutdown with configurable delay, environment-aware shutdown strategy
- **Usage**: Used by `/stop_server` endpoints in both applications

### clean_environment.py - Environment Cleanup Script
- **Purpose**: Automated cleanup of testing environment after CI/CD pipeline execution
- **Features**: Graceful service shutdown via HTTP endpoints, log file cleanup, database reset, temp file removal
- **Usage**: `python clean_environment.py`

## Testing Suite

### Prerequisites for Testing
1. MySQL Docker container must be running
2. Virtual environment activated
3. Dependencies installed

### 1. Backend Testing (backend_testing.py)

Tests the REST API endpoints:

```bash
python backend_testing.py
```

**Test Flow:**
- Verifies MySQL Docker container status
- Starts REST API server automatically
- Tests POST, GET, PUT, DELETE operations
- Verifies database consistency
- Automatic server cleanup

### 2. Frontend Testing (frontend_testing.py)

Tests the web interface using Selenium:

```bash
python frontend_testing.py
```

**Test Flow:**
- Initializes database with `setup_test_db.py`
- Loads configuration from database `config` table
- Starts web application automatically
- Tests browser interaction (Chrome/Firefox support)
- Verifies HTML element display
- Database-driven test parameters

### 3. Combined End-to-End Testing (combined_testing.py)

Complete user lifecycle testing:

```bash
python combined_testing.py
```

**Test Flow:**
- Starts both REST API and web interface servers
- Creates user via API
- Verifies user in database
- Tests web interface display
- Automatic server cleanup on completion/failure

## API Endpoints

### REST API (port 5000)

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/healthz` | Health check endpoint | Returns service status |
| GET | `/stop_server` | Gracefully stop the server | Triggers shutdown |
| POST | `/users` | Create a new user | `{"user_name": "john_doe"}` |
| GET | `/users` | Get all users | Returns list of all users |
| GET | `/users/{user_id}` | Get specific user by ID | `/users/1` |
| PUT | `/users/{user_id}` | Update user information | `{"user_name": "jane_doe"}` |
| DELETE | `/users/{user_id}` | Delete user by ID | `/users/1` |

### Web Interface (port 5001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Health check endpoint |
| GET | `/stop_server` | Gracefully stop the server |
| GET | `/users/get_user_data/{user_id}` | Display user as HTML |

### Example API Usage

**Health check:**
```bash
curl -X GET "http://localhost:5000/healthz"
```

**Stop server:**
```bash
curl -X GET "http://localhost:5000/stop_server"
```

**Create a user:**
```bash
curl -X POST "http://localhost:5000/users" \
     -H "Content-Type: application/json" \
     -d '{"user_name": "john_doe"}'
```

**Get a user:**
```bash
curl -X GET "http://localhost:5000/users/1"
```

**Update a user:**
```bash
curl -X PUT "http://localhost:5000/users/1" \
     -H "Content-Type: application/json" \
     -d '{"user_name": "jane_doe"}'
```

**Delete a user:**
```bash
curl -X DELETE "http://localhost:5000/users/1"
```

## Dependencies

### Core Dependencies
- `fastapi[standard]==0.116.1` - Web framework
- `uvicorn==0.32.0` - ASGI server
- `pydantic==2.9.2` - Data validation
- `pymysql==1.1.1` - MySQL database driver
- `python-dotenv` - Environment variable loading

### Testing Dependencies
- `requests==2.31.0` - HTTP client for API testing
- `selenium==4.34.2` - Web browser automation
- `webdriver-manager==4.0.2` - Automatic WebDriver management

## Key Features

### Security Enhancements
- **SQL Injection Protection**: All database queries use prepared statements
- **Input Validation**: Pydantic models ensure data integrity
- **Environment Variables**: Sensitive data stored in `.env` file
- **Custom Error Handling**: 404 error handlers for non-existing routes in both applications

### Configuration Management
- **Database-Driven Testing**: Test parameters stored in `config` table
- **Dynamic Browser Support**: Chrome and Firefox support
- **Flexible Configuration**: Environment variables for all settings

### Automation Features
- **Auto-Initialization**: Tests automatically set up databases and servers
- **Docker Integration**: MySQL container status verification
- **Process Management**: Automatic server startup and cleanup
- **Comprehensive Testing**: Backend, frontend, and end-to-end coverage
- **Graceful Shutdown**: Health check and server stop endpoints for controlled shutdown
- **Environment Cleanup**: Automated cleanup script for CI/CD pipelines

## Troubleshooting

### Common Issues

1. **MySQL Connection Failed:**
   - Verify container is running: `docker ps | grep mysql`
   - Check credentials in `.env` file
   - Restart container: `docker restart mysql-container`
   - Check logs: `docker logs mysql-container`

2. **Port Already in Use:**
   - Change PORT/WEB_PORT in `.env` file
   - Kill existing processes: `lsof -ti:5000 | xargs kill -9`

3. **Module Import Errors:**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Browser Driver Issues:**
   - WebDriver Manager automatically downloads drivers
   - Ensure Chrome or Firefox is installed
   - Check firewall/antivirus blocking downloads

5. **Test Database Issues:**
   - Run `setup_test_db.py` to reset database
   - Verify MySQL container has proper permissions
   - Check database name matches `.env` configuration

### Logs and Debugging

- Application logs are displayed in console
- MySQL container logs: `docker logs mysql-container`
- Enable debug mode by setting `RELOAD=true` in `.env`

## Development Notes

- All applications load environment variables from `.env` file
- MySQL Docker container must be running for all operations
- Testing framework automatically manages server lifecycles
- Configuration-driven approach eliminates hardcoded values
- Prepared statements protect against SQL injection attacks

## License

This project is for educational/development purposes.