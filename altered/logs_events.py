import os
import logging
from datetime import datetime

# Create a dedicated logger for events.
event_logger = logging.getLogger("event_logger")
event_logger.setLevel(logging.INFO)

def init_event_logger(logs_path: str, logs_name: str) -> None:
    """
    Initializes event logging by creating a dedicated logger with its own
    file handler and formatter. This configuration ensures that only one log
    file per day is created. If a file for today exists, it is reused.
    A header line containing the runtime timestamp is written to a new file.
    
    Args:
        logs_path: (str) Directory where the log file will be stored.
        logs_name: (str) Name of the event log file (should include a full 
                     timestamp, e.g. "2025-03-14_18-04-17_events.log").
    """
    os.makedirs(logs_path, exist_ok=True)
    today_str = datetime.now().strftime('%Y-%m-%d')
    existing_file = None
    for file in os.listdir(logs_path):
        if file.startswith(today_str) and file.endswith("_events.log"):
            existing_file = file
            break
    if existing_file:
        log_file_path = os.path.join(logs_path, existing_file)
    else:
        log_file_path = os.path.join(logs_path, logs_name)
        # Write header with runtime timestamp.
        runtime_stamp = logs_name.split("_events.log")[0]
        with open(log_file_path, "w") as f:
            f.write(f"runtime: {runtime_stamp}\n")
    
    # Remove any previously attached handlers for this logger.
    if event_logger.hasHandlers():
        event_logger.handlers.clear()

    file_handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    event_logger.addHandler(file_handler)

def logprint(message: str) -> None:
    """
    Logs a given message using the dedicated event logger and prints it.
    
    Args:
    """
    event_logger.info(message)
