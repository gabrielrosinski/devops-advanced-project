# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive FastAPI-based application suite with:
- **REST API** (`rest_app.py`) - Full CRUD endpoints for user management on port 5000
- **Web Interface** (`web_app.py`) - HTML user display interface on port 5001
- **Database Layer** (`db_connector.py`) - MySQL connection and operations
- **Testing Suite** - Backend, frontend, and combined end-to-end testing
- **Configuration Management** - Database-driven test configuration

## Development Setup

The project uses Poetry for dependency management:
- Dependencies: defined in `pyproject.toml`
- Poetry manages virtual environments automatically

### Setting up the environment:
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

### Alternative setup with pip (current):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Database Setup

**Prerequisites:** MySQL Docker container must be running

Initialize the database and test data:
```bash
python setup_test_db.py
```

This creates:
- `users` table with user management data
- `config` table with test configuration (API URLs, browser types, test users)

## Running the Applications

### REST API Server
```bash
python rest_app.py
```
- Host: `0.0.0.0` (HOST env var)
- Port: `5000` (PORT env var)
- Reload: `true` (RELOAD env var)

### Web Interface Server
```bash
python web_app.py
```
- Host: `127.0.0.1` (HOST env var)
- Port: `5001` (WEB_PORT env var)

## API Endpoints

### REST API (port 5000)
- `POST /users` - Create a new user
- `GET /users` - Get all users
- `GET /users/{user_id}` - Get specific user by ID
- `PUT /users/{user_id}` - Update user information
- `DELETE /users/{user_id}` - Delete user by ID

### Web Interface (port 5001)
- `GET /users/get_user_data/{user_id}` - Display user information as HTML

## Testing Suite

### Backend Testing
```bash
python backend_testing.py
```
- Checks MySQL Docker container status
- Starts REST API server automatically
- Tests all CRUD operations
- Verifies database consistency

### Frontend Testing
```bash
python frontend_testing.py
```
- Initializes database with `setup_test_db.py`
- Loads configuration from database `config` table
- Starts web application automatically
- Supports dynamic browser selection (Chrome/Firefox)
- Database-driven test parameters

### Combined End-to-End Testing
```bash
python combined_testing.py
```
- Starts both REST API and web interface servers
- Complete user lifecycle testing
- API → Database → Web interface verification
- Automatic server cleanup on completion

## Dependencies

Key packages used:
- `fastapi[standard]==0.116.1` - Web framework
- `uvicorn==0.32.0` - ASGI server
- `pydantic==2.9.2` - Data validation
- `requests==2.31.0` - HTTP client
- `pymysql==1.1.1` - MySQL database driver
- `selenium==4.34.2` - Web automation
- `webdriver-manager==4.0.2` - WebDriver management

## Key Features

### Security Enhancements
- **SQL Injection Protection**: All database queries use prepared statements with parameterized inputs
- **Secure Database Operations**: Input validation and sanitization throughout

### Configuration Management
- **Database-Driven Testing**: Test parameters stored in `config` table
- **Dynamic Browser Support**: Chrome and Firefox support via configuration
- **Environment Variables**: Configurable hosts, ports, and settings

### Automation Features
- **Auto-Initialization**: Tests automatically set up required databases and servers
- **Docker Integration**: MySQL container status verification
- **Process Management**: Automatic server startup and cleanup
- **Comprehensive Testing**: Backend, frontend, and end-to-end test coverage

## Project Structure

```
├── rest_app.py           # REST API server (port 5000)
├── web_app.py            # Web interface server (port 5001)
├── db_connector.py       # Database connection and operations
├── setup_test_db.py      # Database initialization
├── backend_testing.py    # REST API testing
├── frontend_testing.py   # Web interface testing
├── combined_testing.py   # End-to-end testing
├── requirements.txt      # Python dependencies
└── .env                  # Environment configuration
```

## Notes

- All applications load environment variables from `.env` file using `python-dotenv`
- MySQL Docker container must be running for database operations
- Testing framework automatically manages server lifecycles
- Configuration-driven approach eliminates hardcoded test values