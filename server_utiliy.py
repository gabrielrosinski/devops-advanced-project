import os
import signal
import asyncio
from fastapi import HTTPException

async def shutdown_server():
    "Perform graceful shutdown after a brief delay"
    
    try:
        await asyncio.sleep(1)
        if os.getenv("RELOAD", "true").lower() == "true":
            os._exit(0)  # Force exit in development mode
        else:
            os.kill(os.getpid(), signal.SIGTERM)  # Graceful in production
    except Exception as e:
        print(f"Error during shutdown: {e}")
        os._exit(0)    # Fallback to force shutdown    