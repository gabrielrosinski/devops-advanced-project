#!/usr/bin/env python3
"""
Environment Cleanup Script

This script cleans up the testing environment after CI/CD pipeline execution.
It handles stopping background processes, cleaning up files, and resetting database state.

Usage:
    python clean_environment.py
"""

import os
import sys
import signal
import subprocess
import time
from typing import List, Optional

def find_processes_by_name(process_name: str) -> List[int]:
    """Find process IDs by process name pattern.

    Args:
        process_name (str): Process name pattern to search for

    Returns:
        List[int]: List of process IDs
    """
    try:
        result = subprocess.run(
            ['pgrep', '-f', process_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return [int(pid) for pid in result.stdout.strip().split('\n') if pid]
        return []
    except Exception as e:
        print(f"Error finding processes: {e}")
        return []

def stop_process_gracefully(pid: int, timeout: int = 5) -> bool:
    """Stop a process gracefully with SIGTERM, then SIGKILL if needed.

    Args:
        pid (int): Process ID to stop
        timeout (int): Timeout in seconds before force kill

    Returns:
        bool: True if process was stopped successfully
    """
    try:
        # Check if process exists
        os.kill(pid, 0)

        # Send SIGTERM for graceful shutdown
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM to process {pid}")

        # Wait for graceful shutdown
        for _ in range(timeout):
            try:
                os.kill(pid, 0)  # Check if process still exists
                time.sleep(1)
            except OSError:
                print(f"Process {pid} terminated gracefully")
                return True

        # Force kill if still running
        try:
            os.kill(pid, signal.SIGKILL)
            print(f"Force killed process {pid}")
            return True
        except OSError:
            print(f"Process {pid} already terminated")
            return True

    except OSError:
        # Process doesn't exist
        return True
    except Exception as e:
        print(f"Error stopping process {pid}: {e}")
        return False

def cleanup_background_services():
    """Stop background Python services (REST API and Web App)."""
    print("=== Stopping Background Services ===")

    services = [
        "python rest_app.py",
        "python web_app.py"
    ]

    for service in services:
        print(f"Looking for processes: {service}")
        pids = find_processes_by_name(service)

        if pids:
            print(f"Found {len(pids)} process(es): {pids}")
            for pid in pids:
                stop_process_gracefully(pid)
        else:
            print(f"No processes found for: {service}")

    print("Background services cleanup completed")

def cleanup_log_files():
    """Remove log files created during testing."""
    print("\n=== Cleaning Up Log Files ===")

    log_files = [
        "server.log",
        "web.log",
        "nohup.out"
    ]

    for log_file in log_files:
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
                print(f"Removed: {log_file}")
            else:
                print(f"Not found: {log_file}")
        except Exception as e:
            print(f"Error removing {log_file}: {e}")

    print("Log files cleanup completed")

def cleanup_database():
    """Clear test data from database while preserving schema."""
    print("\n=== Cleaning Database ===")

    try:
        from db_connector import Database
        Database.clear_data()
        print("Database test data cleared successfully")
    except ImportError:
        print("Warning: db_connector module not found, skipping database cleanup")
    except Exception as e:
        print(f"Database cleanup failed: {e}")

def cleanup_temp_files():
    """Remove temporary files that might be created during testing."""
    print("\n=== Cleaning Temporary Files ===")

    temp_patterns = [
        "*.pyc",
        "__pycache__",
        ".pytest_cache",
        "*.tmp",
        ".coverage"
    ]

    for pattern in temp_patterns:
        try:
            if pattern == "__pycache__":
                # Remove __pycache__ directories
                result = subprocess.run(['find', '.', '-name', '__pycache__', '-type', 'd'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for cache_dir in result.stdout.strip().split('\n'):
                        if cache_dir:
                            subprocess.run(['rm', '-rf', cache_dir])
                            print(f"Removed: {cache_dir}")
            else:
                # Remove files matching pattern
                result = subprocess.run(['find', '.', '-name', pattern, '-type', 'f'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for temp_file in result.stdout.strip().split('\n'):
                        if temp_file:
                            os.remove(temp_file)
                            print(f"Removed: {temp_file}")
        except Exception as e:
            print(f"Error cleaning {pattern}: {e}")

    print("Temporary files cleanup completed")

def show_remaining_processes():
    """Display any remaining Python processes for debugging."""
    print("\n=== Remaining Python Processes ===")

    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if result.returncode == 0:
            python_processes = [line for line in result.stdout.split('\n') if 'python' in line.lower()]
            if python_processes:
                for process in python_processes:
                    print(process)
            else:
                print("No Python processes found")
    except Exception as e:
        print(f"Error listing processes: {e}")

def main():
    """Main cleanup function."""
    print("Starting Environment Cleanup...")
    print("=" * 50)

    try:
        # Cleanup in order of importance
        cleanup_background_services()
        cleanup_log_files()
        cleanup_database()
        cleanup_temp_files()
        show_remaining_processes()

        print("\n" + "=" * 50)
        print("✅ Environment cleanup completed successfully!")

    except KeyboardInterrupt:
        print("\n❌ Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Cleanup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()