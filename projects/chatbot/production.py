"""
Production entry point for CortexChat Windows service
"""
import uvicorn
import logging
import os
from pathlib import Path

# Configure logging for production
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "cortexchat.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting CortexChat in production mode...")

    # Get configuration from environment with defaults
    host = os.getenv("CHAT_HOST", "127.0.0.1")
    port = int(os.getenv("CHAT_PORT", "8001"))
    workers = int(os.getenv("CHAT_WORKERS", "4"))

    logger.info(f"Server configuration: {host}:{port} with {workers} workers")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        log_level="info",
        access_log=True,
        reload=False  # Important: disable reload in production
    )