"""
Entry point to run the Sales Analytics AI Agent application
"""
import os
import sys
from pathlib import Path
import uvicorn
from app.core.config import settings
from app.core.logger import app_logger as logger

# Add the project root to the Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

# Import and run the application
if __name__ == "__main__":
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Server will run at http://{settings.HOST}:{settings.PORT}")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower()
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
