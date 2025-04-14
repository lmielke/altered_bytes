#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
"""
Background runner and controller for a monitored user activity script.

Provides:
- Background execution of a target script.
- Singleton pattern for the runner using a PID file.
- System tray icon for status info and stopping.
- Command-line interface for start/stop/info.
"""

import ctypes
import os
import sys
import subprocess
import psutil
import time
import re
from pystray import Icon, MenuItem, Menu
from PIL import Image
import threading
from datetime import datetime as dt
import atexit
import logging

# --- Basic Logging Setup ---
# Log messages to stderr for visibility when run with python.exe
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    stream=sys.stderr)

# --- Constants ---
SCRIPT_NAME = os.path.basename(sys.argv[0]) # Detect script name
PID_FILENAME = f"{SCRIPT_NAME}.pid"

# Determine script directory safely
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

PID_SUBDIR = os.path.join(SCRIPT_DIR, "resources", "logs", "activities")
PID_FILE = os.path.join(PID_SUBDIR, PID_FILENAME)

# TODO: Make DEFAULT_EXECUTABLE configurable or detect automatically
DEFAULT_EXECUTABLE = os.path.expanduser(
    "~/.virtualenvs/altered_bytes-uZ3fI-DB/Scripts/pythonw.exe"
)
MONITORED_MODULE = "altered.info_app_hist_clicks" # Target script/module

# Instance ID for the monitored process (used for pattern matching)
INSTANCE_ID = f"bg_run:{dt.now().strftime('%Y-%m-%d_%H%M%S')}"
INSTANCE_PATTERN = re.compile(r"bg_run:\d{4}-\d{2}-\d{2}_\d{6}")

# --- Utility Functions ---

def safe_remove_pid_file():
    """Removes the PID file if it exists, ignoring errors."""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            logging.info(f"Removed PID file: {PID_FILE}")
    except OSError as e:
        # Non-critical if removal fails, log it
        logging.warning(f"Error removing PID file {PID_FILE}: {e}")

# Register cleanup function to run on normal exit
atexit.register(safe_remove_pid_file)

def terminate_process(pid: int, description: str = "process"):
    """Attempts to gracefully terminate, then kill, a specific PID."""
    if pid is None:
        return
    logging.info(f"Attempting to stop {description} (PID: {pid})...")
    try:
        proc = psutil.Process(pid)
        proc.terminate()  # Ask nicely first
        try:
            proc.wait(timeout=2)  # Wait up to 2 seconds for graceful exit
            logging.info(f"{description.capitalize()} (PID: {pid}) terminated.")
        except psutil.TimeoutExpired:
            logging.warning(
                f"{description.capitalize()} (PID: {pid}) did not stop "
                f"gracefully, killing."
            )
            proc.kill()  # Force kill
    except psutil.NoSuchProcess:
        logging.info(f"{description.capitalize()} (PID: {pid}) already stopped.")
    except (psutil.AccessDenied, OSError) as e:
        logging.error(f"Error stopping {description} (PID: {pid}): {e}")
    except Exception as e:
        # Catch any other unexpected errors during termination
        logging.error(f"Unexpected error stopping {description} (PID: {pid}): {e}")

# --- Core Logic Functions ---

def write_pid_file():
    """Writes the current process ID to the PID file."""
    pid = os.getpid()
    try:
        os.makedirs(PID_SUBDIR, exist_ok=True) # Ensure directory exists
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
        logging.info(f"Runner PID {pid} written to {PID_FILE}")
    except (IOError, OSError) as e:
        logging.error(f"Failed to write PID file {PID_FILE}: {e}")
        ctypes.windll.user32.MessageBoxW(
            0, f"Fatal: Could not write PID file:\n{PID_FILE}\nError: {e}",
            "PID Error", 16 # MB_ICONERROR
        )
        raise SystemExit(f"Could not write PID file {PID_FILE}")

def is_runner_already_active() -> bool:
    """Checks if a runner process listed in the PID file is active."""
    if not os.path.exists(PID_FILE):
        return False

    pid = None
    try:
        with open(PID_FILE, 'r') as f:
            pid_str = f.read().strip()
            if not pid_str.isdigit():
                raise ValueError("Non-integer content")
            pid = int(pid_str)
    except (IOError, ValueError) as e:
        logging.warning(f"Invalid/unreadable PID file {PID_FILE}: {e}. Cleaning up.")
        safe_remove_pid_file()
        return False

    try:
        proc = psutil.Process(pid)
        # Basic check: is it running and a python process running our script?
        exe_name = os.path.basename(proc.exe()).lower()
        # Check if SCRIPT_NAME is part of any command line argument
        script_in_cmdline = any(SCRIPT_NAME in part for part in proc.cmdline())

        if proc.is_running() and ('python' in exe_name) and script_in_cmdline:
            logging.info(f"Found active runner process (PID: {pid}).")
            return True
        else:
            logging.warning(
                f"Stale PID {pid} found (process not running or not '{SCRIPT_NAME}'). "
                f"Cleaning up."
            )
            safe_remove_pid_file()
            return False
    except psutil.NoSuchProcess:
        logging.warning(f"PID {pid} not found. Cleaning up stale PID file.")
        safe_remove_pid_file()
        return False
    except (psutil.AccessDenied, OSError) as e:
        logging.error(
            f"Cannot check process {pid} (Error: {e}). "
            f"Assuming active to prevent duplicates."
        )
        # Safer to assume active if unsure
        return True

def stop_monitor_processes():
    """Stops monitored background processes matching the INSTANCE_PATTERN."""
    logging.info("Stopping monitor processes matching pattern...")
    stopped_count = 0
    # Get a snapshot of processes to avoid issues with iterator changing
    procs_to_check = list(psutil.process_iter(attrs=['pid', 'cmdline']))
    for proc_info in procs_to_check:
        cmdline = proc_info.info.get('cmdline')
        pid = proc_info.info.get('pid')
        if not cmdline or pid is None:
            continue

        try:
            cmdline_str = ' '.join(cmdline)
            if INSTANCE_PATTERN.search(cmdline_str):
                terminate_process(pid, f"monitor process {pid}")
                stopped_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue # Process already gone or inaccessible
        except Exception as e:
            logging.error(f"Error processing PID {pid} during stop scan: {e}")
    logging.info(f"Finished stopping monitor processes. Found {stopped_count}.")

def run_monitored_script_detached():
    """Launches the target monitoring script in the background."""
    python_command = [
        DEFAULT_EXECUTABLE,
        "-m", MONITORED_MODULE,
        "-id", INSTANCE_ID
    ]
    logging.info(f"Launching monitor: {' '.join(python_command)}")
    try:
        subprocess.Popen(
            python_command,
            stdout=subprocess.DEVNULL, # Prevent blocking on output
            stderr=subprocess.DEVNULL, # Prevent blocking on output
            stdin=subprocess.DEVNULL,
            # Ensure the new process runs independently
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    except FileNotFoundError:
        logging.error(f"Failed: Executable not found at {DEFAULT_EXECUTABLE}")
        ctypes.windll.user32.MessageBoxW(
            0, f"Error: Python executable not found:\n{DEFAULT_EXECUTABLE}",
            "Startup Error", 16 # MB_ICONERROR
        )
    except Exception as e:
        logging.error(f"Failed to start monitor process: {e}")
        # Log only, don't show message box for general errors here

def create_tray_image() -> Image.Image:
    """Loads the icon image, providing a fallback."""
    # Consider making icon path configurable
    icon_path = os.path.join(SCRIPT_DIR, 'resources', 'images', 'eye_thumb.png')
    try:
        return Image.open(icon_path)
    except Exception as e:
        logging.warning(f"Failed to load icon '{icon_path}': {e}. Using fallback.")
        try:
            # Simple red square fallback
            img = Image.new('RGB', (64, 64), color = 'red')
            return img
        except Exception as pil_fallback_err:
            logging.error(f"PIL fallback image creation failed: {pil_fallback_err}")
            return None # pystray should handle None if PIL is totally broken

# --- Info Gathering and Display ---

def get_info_message() -> str:
    """Gathers process information and returns a formatted string."""
    logging.info("Gathering process information...")
    runner_active = os.path.exists(PID_FILE)
    monitored_lines = []
    msg = ""

    try:
        procs_to_check = list(psutil.process_iter(attrs=['pid', 'cmdline']))
        for proc_info in procs_to_check:
            cmdline = proc_info.info.get('cmdline')
            pid = proc_info.info.get('pid')
            if not cmdline or pid is None:
                continue

            try:
                cmdline_str = ' '.join(cmdline)
                if INSTANCE_PATTERN.search(cmdline_str):
                    # Limit line length for display clarity
                    display_line = (
                        cmdline_str[:85] + '...'
                        if len(cmdline_str) > 85 else cmdline_str
                    )
                    monitored_lines.append(f"  - PID {pid}: {display_line}")
            except Exception as inner_e:
                 logging.warning(f"Could not process cmdline for PID {pid}: {inner_e}")

    except Exception as e:
        logging.error(f"Failed to iterate processes for info: {e}")
        monitored_lines.append("  - Error retrieving process list.")

    # Build the final message string
    if monitored_lines:
        msg = "Monitored processes found:\n" + "\n".join(monitored_lines)
    elif runner_active:
        msg = "Runner active (PID file exists).\nNo monitored processes found."
    else:
        msg = "Neither runner nor monitored processes found."
    logging.info("Finished gathering process information.")
    return msg

def show_info_message_box(info_message: str, title: str):
    """Displays the info message box."""
    logging.info("Displaying info message box.")
    try:
        # Use standard Windows information icon
        ctypes.windll.user32.MessageBoxW(0, info_message, title, 64) # MB_ICONINFORMATION
    except Exception as e:
        logging.error(f"Failed to display info message box: {e}")

# --- Tray Icon Callbacks ---

def on_tray_info(icon: Icon, item: MenuItem):
    """Callback for tray; Gathers info and displays msg box in a thread."""
    logging.info("Info requested via tray icon.")
    msg = get_info_message() # Gather info

    # Start message box in a new thread to avoid blocking tray thread
    logging.info("Starting info message box display thread for tray.")
    msg_thread = threading.Thread(
        target=show_info_message_box,
        args=(msg, f"{SCRIPT_NAME} Info"),
        daemon=True # OK for this thread not to block exit
    )
    msg_thread.start()

def on_tray_stop(icon: Icon, item: MenuItem):
    """Stops monitor processes and the tray icon/runner."""
    logging.info("Stop requested via tray icon.")
    stop_monitor_processes() # Stop the background monitored process(es)
    logging.info("Stopping tray icon...")
    icon.stop() # Stop the tray icon event loop, script exits via atexit

# --- Main Execution Functions ---

def run_tray_icon():
    """Creates and runs the system tray icon's event loop."""
    icon = Icon(f"{SCRIPT_NAME}_instance") # Unique name for pystray
    icon.icon = create_tray_image()
    icon.title = "User Activity Monitoring" # Tooltip
    icon.menu = Menu(
        MenuItem("Info", on_tray_info),
        MenuItem("Stop", on_tray_stop)
    )
    logging.info("Starting tray icon event loop...")
    try:
        # This blocks until icon.stop() is called
        icon.run()
    except Exception as e:
        logging.exception("Tray icon thread encountered an unhandled error.")
        # Consider implications: If tray crashes, script might linger.
        # Maybe attempt self-termination?
        # safe_remove_pid_file() # Clean up PID if tray crashes? Risky.
        # os._exit(1) # Force exit? Also risky.
    logging.info("Tray icon event loop finished.")

def main(command: str):
    """Handles command-line arguments and main application logic."""
    if command == "start":
        logging.info("Command: start")
        if is_runner_already_active():
            logging.warning("Runner already active, exiting.")
            # Use warning icon for "Already Running" message
            ctypes.windll.user32.MessageBoxW(
                0, f"{SCRIPT_NAME} is already running.",
                "Already Running", 48 # MB_ICONWARNING
            )
            return

        write_pid_file() # Create PID file *before* launching background tasks
        run_monitored_script_detached()
        # Start tray icon in non-daemon thread to keep script alive
        tray_thread = threading.Thread(target=run_tray_icon, daemon=False)
        tray_thread.start()

    elif command == "stop":
        logging.info("Command: stop")
        # 1. Stop the monitored background process(es) first
        stop_monitor_processes()

        # 2. Stop the runner process itself using the PID file
        if not os.path.exists(PID_FILE):
            logging.warning("Runner PID file not found. Cannot stop runner.")
            return

        pid_to_stop = None
        try:
            with open(PID_FILE, 'r') as f:
                pid_str = f.read().strip()
                if not pid_str.isdigit():
                    raise ValueError("Non-integer content")
                pid_to_stop = int(pid_str)

            # Attempt termination of the runner process
            terminate_process(pid_to_stop, "runner process")

            # Explicitly remove PID file here, as runner's atexit might not run
            safe_remove_pid_file()

        except (IOError, ValueError) as e:
            logging.error(f"Error reading/parsing PID file {PID_FILE}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during command-line stop: {e}")

    elif command == "info":
        logging.info("Command: info")
        # Gather info and display message box directly (no thread needed here)
        msg = get_info_message()
        show_info_message_box(msg, f"{SCRIPT_NAME} Info")

# --- Script Entry Point ---
if __name__ == "__main__":
    # Basic check for running as administrator (optional, but good for psutil)
    try:
        is_admin = os.getuid() == 0 # Linux/Mac check
    except AttributeError:
        try:
            # Windows check
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
             is_admin = False # Assume not admin if check fails
    log_level_prefix = "[ADMIN] " if is_admin else ""

    logging.info(f"--- {log_level_prefix}{SCRIPT_NAME} starting ({' '.join(sys.argv)}) ---")
    command_to_run = "start" # Default command

    try:
        if len(sys.argv) > 2:
            raise ValueError("Too many arguments.")
        if len(sys.argv) == 2:
            arg = sys.argv[1].lower()
            if arg not in ["start", "stop", "info"]:
                raise ValueError(f"Invalid command: '{arg}'. Use start, stop, or info.")
            command_to_run = arg

        # Execute the main logic based on the command
        main(command=command_to_run)

    except SystemExit as e:
        # Raised by write_pid_file on critical error
        logging.info(f"Script explicitly exiting: {e}")
        # Ensure PID file is removed if SystemExit happened after writing it
        if command_to_run == "start" and os.path.exists(PID_FILE):
             pid_in_file = -1
             try:
                 with open(PID_FILE,'r') as f: pid_in_file = int(f.read().strip())
             except: pass
             if pid_in_file == os.getpid(): # Only remove if it's ours
                 safe_remove_pid_file()
        sys.exit(e.code if isinstance(e.code, int) else 1)
    except KeyboardInterrupt:
        logging.warning("Script interrupted by user (Ctrl+C).")
        # Cleanup handled by atexit mostly
        sys.exit(1)
    except Exception as e:
        logging.exception("FATAL ERROR in main execution.") # Log full traceback
        # Display error message to user
        ctypes.windll.user32.MessageBoxW(
            0, f"SCRIPT ERROR:\n{type(e).__name__}: {e}",
            f"{SCRIPT_NAME} Failed", 16 # MB_ICONERROR
        )
        # Attempt cleanup if possible, atexit might still run but be cautious
        safe_remove_pid_file()
        sys.exit(1) # Indicate error exit

    logging.info(f"--- {SCRIPT_NAME} execution finished ({command_to_run}) ---")