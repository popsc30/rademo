import sys
from loguru import logger
from pathlib import Path

def setup_logging(env: str = "dev"):
    """Configure logging settings for the application.

    Args:
        env (str): The current environment (e.g., "dev", "test", "prod").
    """
    logger.remove() # Remove default handler

    console_log_levels = {
        "dev": "DEBUG",
        "test": "INFO",
        "prod": "WARNING",
    }
    console_level = console_log_levels.get(env, "DEBUG")

    log_dir = Path("./logs") # Relative path or dynamically determined PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    # Basic log format for files and console
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " \
                 "<level>{level: <5}</level> | " \
                 "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | " \
                 "<level>{message}</level>"

    # File handler for DEBUG level logs (more detailed, longer retention)
    logger.add(
        log_dir / "app-debug.log",
        rotation="10 MB",     # Rotate every 10 MB
        retention="10 days",  # Keep logs for 10 days
        compression="zip",    # Compress old logs
        level="DEBUG",
        format=log_format,
        enqueue=False,         # Use a separate thread for logging (non-blocking)
        filter=lambda record: record["level"].name == "DEBUG"
    )

    # File handler for INFO level and above (general application logs)
    logger.add(
        log_dir / "app.log",
        rotation="10 MB",
        retention="1 days",
        compression="zip",
        level="INFO",
        format=log_format,
        enqueue=False,
    )

    # Console handler (stderr) with colorization, level based on environment
    logger.add(
        sys.stderr,
        level=console_level,
        format= "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " \
                 "<level>{level: <5}</level> | " \
                 "<cyan>{file}</cyan>:<cyan>{line}</cyan> | " \
                 "<level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True
    )
