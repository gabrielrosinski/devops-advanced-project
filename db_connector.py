"""
Database Connection Module

This module provides database connection management and initialization for MySQL databases.
It handles user authentication, database schema creation, and connection pooling.

Classes:
    Database: Main database connection and management class

Dependencies:
    - pymysql: MySQL database driver
    - python-dotenv: Environment variable management

Environment Variables:
    DB_HOST: Database host (default: localhost)
    DB_USER: Database username (default: username)
    DB_PASSWORD: Database password (default: password)
    DB_NAME: Database name (default: mydb)
    DB_ROOT_USER: Root user for admin operations (default: root)
    DB_ROOT_PASSWORD: Root password for admin operations (default: '')

Usage:
    >>> db = Database()
    >>> conn = db.get_connection()
    >>> cursor = conn.cursor()
"""

import pymysql
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Database:
    """Database connection and management class.

    Provides methods for connecting to MySQL databases, managing admin connections,
    creating users, and initializing database schemas.

    Attributes:
        config (dict): Database connection configuration
        admin_connection: Administrative database connection
    """

    def __init__(self):
        """Initialize Database instance with configuration from environment variables."""
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'username'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'database': os.getenv('DB_NAME', 'mydb')
        }
        self.admin_connection = None

    def get_connection(self):
        """Get a database connection, initializing schema if needed.

        Returns:
            pymysql.Connection: Active database connection

        Raises:
            Exception: If connection cannot be established
        """
        try:
            conn = pymysql.connect(**self.config)
            if conn is None:
                raise Exception("Failed to establish database connection")
                
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE 'users'")
                table_exists = cursor.fetchone()
                if table_exists is not None:
                    return conn
            conn.close()
        except Exception as e:
            print(f"Database connection failed: {e}")
        
        self.initialize_database()
        
        final_conn = pymysql.connect(**self.config)
        if final_conn is None:
            raise Exception("Critical: Unable to establish database connection after initialization")
        return final_conn

    def connect_as_admin(self, admin_user: str = "root", admin_password: str = "") -> bool:
        """Connect to database with administrative privileges.

        Args:
            admin_user (str): Admin username (default: 'root')
            admin_password (str): Admin password (default: '')

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.admin_connection = pymysql.connect(
                host=self.config['host'],
                user=admin_user,
                password=admin_password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return True
        except Exception as e:
            print(f"Failed to connect as admin: {e}")
            return False

    def create_root_user(self, username: str, password: str, host: str = '%') -> bool:
        """Create a new root user with full privileges.

        Args:
            username (str): Username for the new root user
            password (str): Password for the new root user
            host (str): Host pattern for user access (default: '%')

        Returns:
            bool: True if user created successfully, False otherwise
        """
        if not self.admin_connection:
            print("Not connected as admin")
            return False
        
        try:
            with self.admin_connection.cursor() as cursor:
                cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'{host}' IDENTIFIED BY '{password}'")
                cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{username}'@'{host}' WITH GRANT OPTION")
                cursor.execute("FLUSH PRIVILEGES")
                self.admin_connection.commit()
                print(f"Root user '{username}' created successfully")
                return True
        except Exception as e:
            print(f"Failed to create root user: {e}")
            return False

    def create_database_schema(self, database_name: str, schema_file: Optional[str] = None) -> bool:
        """Create database and initialize schema.

        Args:
            database_name (str): Name of database to create
            schema_file (Optional[str]): Path to SQL schema file

        Returns:
            bool: True if schema created successfully, False otherwise
        """
        if not self.admin_connection:
            print("Not connected as admin")
            return False
        
        try:
            with self.admin_connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
                cursor.execute(f"USE {database_name}")
                
                if schema_file and os.path.exists(schema_file):
                    with open(schema_file, 'r') as f:
                        schema_sql = f.read()
                    
                    for statement in schema_sql.split(';'):
                        statement = statement.strip()
                        if statement:
                            cursor.execute(statement)
                else:
                    self._create_default_schema(cursor)
                
                self.admin_connection.commit()
                print(f"Database '{database_name}' and schema created successfully")
                return True
        except Exception as e:
            print(f"Failed to create database schema: {e}")
            return False

    def _create_default_schema(self, cursor) -> None:
        """Create default database schema with users table.

        Args:
            cursor: Database cursor for executing SQL statements
        """
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)

    def initialize_database(
        self,
        admin_user: Optional[str] = None,
        admin_password: Optional[str] = None,
        database_name: Optional[str] = None,
        new_root_user: Optional[str] = None,
        new_root_password: Optional[str] = None,
        schema_file: Optional[str] = None
    ) -> bool:
        """Initialize complete database setup.

        Args:
            admin_user (Optional[str]): Admin username
            admin_password (Optional[str]): Admin password
            database_name (Optional[str]): Database name to create
            new_root_user (Optional[str]): New root user to create
            new_root_password (Optional[str]): Password for new root user
            schema_file (Optional[str]): Path to schema SQL file

        Returns:
            bool: True if initialization successful, False otherwise
        """
        admin_user = admin_user or os.getenv('DB_ROOT_USER', 'root')
        admin_password = admin_password or os.getenv('DB_ROOT_PASSWORD', '')
        database_name = database_name or os.getenv('DB_NAME', 'users_db')
        
        if not self.connect_as_admin(admin_user, admin_password):
            return False
        
        try:
            if new_root_user and new_root_password:
                if not self.create_root_user(new_root_user, new_root_password):
                    return False
            
            if not self.create_database_schema(database_name, schema_file):
                return False
            
            print("Database initialization completed successfully")
            return True
        finally:
            self.close_admin_connection()

    def close_admin_connection(self) -> None:
        """Close the administrative database connection."""
        if self.admin_connection:
            self.admin_connection.close()
            self.admin_connection = None
    
