import os
import time
import atexit
import logging
from contextlib import ContextDecorator
from datetime import datetime

# Register shutdown to ensure logging handlers are closed on exit.
atexit.register(logging.shutdown)

class CustomFormatter(logging.Formatter):
    """
    Custom formatter to show only the time (HH:MM:SS,mmm) in log messages.
    """
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        # Use datefmt if provided; otherwise default to "%H:%M:%S"
        s = time.strftime(datefmt or "%H:%M:%S", ct)
        # record.msecs is a float; format it as three-digit integer.
        msecs = int(record.msecs)
        return f"{s},{msecs:03d}"

# Create a dedicated logger for timer logs.
timer_logger = logging.getLogger("timer_logger")
timer_logger.setLevel(logging.INFO)

def init_timer(logs_path: str, logs_name: str) -> None:
    """
    Initializes timer logging. Creates a single file per day by checking
    for an existing file with today's date. If found, it uses that file; if not,
    it creates a new one using the provided logs_name and writes a header line.
    
    Args:
        logs_path: (str) Directory for the log file.
        logs_name: (str) Name of the log file (should include a full timestamp,
                     e.g. "2025-03-14_18-04-17_timer.log").
    """
    os.makedirs(logs_path, exist_ok=True)
    today_str = datetime.now().strftime('%Y-%m-%d')
    existing_file = None
    for file in os.listdir(logs_path):
        if file.startswith(today_str) and file.endswith("_timer.log"):
            existing_file = file
            break
    if existing_file:
        log_file_path = os.path.join(logs_path, existing_file)
    else:
        log_file_path = os.path.join(logs_path, logs_name)
        # Write header if file is new; open in "w" mode to ensure header is at the top.
        runtime_stamp = logs_name.split("_timer.log")[0]
        with open(log_file_path, "w") as f:
            f.write(f"runtime: {runtime_stamp}\n")
    
    # Remove any previously attached handlers for this logger.
    if timer_logger.hasHandlers():
        timer_logger.handlers.clear()
        
    file_handler = logging.FileHandler(log_file_path)
    formatter = CustomFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    timer_logger.addHandler(file_handler)


class Timer(ContextDecorator):
    """Context manager and decorator for timing code blocks.

    Uses time.perf_counter() for high-resolution timing.
    
    Attributes:
        name: (str) A label for the timed block.
    """
    def __init__(self, name: str = "block") -> None:
        self.name = name
        self.start = 0.0

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args, **kwargs) -> bool:
        elapsed = time.perf_counter() - self.start
        timer_logger.info("Elapsed time for %s: %.6f seconds", 
                          self.name, elapsed)
        return False

def timed(name: str = "function"):
    """
    Decorator for timing a function and logging its execution time.

    Args:
        name: (str) A label for the function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            timer_logger.info("Elapsed time for %s: %.6f seconds",
                              name, elapsed)
            return result
        return wrapper
    return decorator
