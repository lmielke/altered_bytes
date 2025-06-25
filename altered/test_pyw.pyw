import ctypes
import os
import sys
import subprocess
import ctypes

def alert() -> None:
    ctypes.windll.user32.MessageBoxW(
        0,
        f"{sys.executable} is running",
        "Test Message",
        0
    )

# import psutil
# import time
# import yaml
# from colorama import Fore, Style, Back

# # Define the path to the PID file and log file
# DEFAULT_DIR = os.path.join(os.path.dirname(__file__), 'resources')
# PID_FILE = os.path.join(DEFAULT_DIR, 'logs', 'your_script.pid')
# NEW_PROCESS_LOG_FILE = os.path.join(DEFAULT_DIR, 'logs', 'activities', 'new_python_processes.yml')
# DEFAULT_EXECUTABLE = f"~/.virtualenvs/altered_bytes-uZ3fI-DB/Scripts/python.exe"

# def get_all_python_processes(*args, verbose:int=0, **kwargs):
#     """
#     Get all running Python (python.exe, pythonw.exe) processes, including command-line arguments.
#     """
#     python_processes, counter = [], 0
#     if verbose:
#         print(f"\n{Fore.YELLOW}Searching for Python processes...{Fore.RESET}")
#     for process in psutil.process_iter(['name', 'pid', 'cmdline']):
#         try:
#             if process.name().lower() in ('python.exe', 'pythonw.exe'):
#                 python_processes.append({
#                     'name': process.name(),
#                     'pid': process.pid,
#                     'cmdline': ' '.join(process.cmdline())  # Capture the command line used to start the process
#                 })
#                 if verbose:
#                     print(f"{counter}: Found {process.name()}, PID {process.pid} ")
#                     if 'Scripts' in process.cmdline():
#                         print(f"command: {process.cmdline().split('Scripts')[-1]}")
#                 counter += 1
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             pass
#     return python_processes

# def log_new_processes(old_processes, new_processes, *args, **kwargs):
#     """
#     Log the new processes that appeared after starting the script.
#     """
#     new_pids = {proc['pid'] for proc in new_processes}
#     old_pids = {proc['pid'] for proc in old_processes}
#     added_processes = [proc for proc in new_processes if proc['pid'] not in old_pids]
#     # Log the added processes to a YAML file
#     if added_processes:
#         with open(NEW_PROCESS_LOG_FILE, "w") as log_file:
#             yaml.dump({f"pid{i+1}": proc['pid'] for i, proc in enumerate(added_processes)}, log_file)
#     else:
#         print("No new processes found.")

# def run_your_script_detached(*args, **kwargs):
#     """
#     Run the script directly using the Python executable without pipenv.
#     """
#     print("Starting the script directly with Python executable...")
#     # Get all Python processes before starting
#     old_python_processes = get_all_python_processes(*args, **kwargs)
#     # Use the Python executable from the current environment
#     python_executable = os.path.expanduser(DEFAULT_EXECUTABLE)
#     # Define the command to run the script directly using the Python executable
#     python_command = [python_executable, "-m", "altered.info_app_hist_activities"]
#     # Run the Python command in a detached mode
#     process = subprocess.Popen(python_command, 
#                                 stdout=subprocess.PIPE, 
#                                 stderr=subprocess.PIPE, 
#                                 stdin=subprocess.DEVNULL
#                                 )

#     # Wait a few seconds to allow the process to start
#     time.sleep(2)
#     # Get all Python processes after starting the subprocess
#     new_python_processes = get_all_python_processes(*args, **kwargs)
#     # Log the new Python processes that appeared
#     log_new_processes(old_python_processes, new_python_processes, *args, **kwargs)
#     print(f"Process started with PID {process.pid} (Python)")

# def stop_your_script(*args, **kwargs):
#     """
#     Stop the script by reading PIDs from the YAML log file.
#     """
#     if not os.path.exists(NEW_PROCESS_LOG_FILE):
#         print("No running process found.")
#         return

#     # Load PIDs from the YAML file
#     with open(NEW_PROCESS_LOG_FILE, "r") as log_file:
#         pids = yaml.safe_load(log_file)
#     for key, pid in pids.items():
#         try:
#             pid = int(pid)
#             print(f"Stopping process with PID: {pid}")
#             process = psutil.Process(pid)
#             process.terminate()  # Gracefully terminate the process
#             process.wait(timeout=5)
#             print(f"Process {pid} terminated successfully.")
#         except psutil.NoSuchProcess:
#             print(f"No process with PID {pid} found.")
#         except psutil.TimeoutExpired:
#             print(f"Process {pid} did not terminate in time.")
#         except Exception as e:
#             print(f"Error terminating process: {e}")

#     # After stopping, remove the log file
#     if os.path.exists(NEW_PROCESS_LOG_FILE):
#         os.remove(NEW_PROCESS_LOG_FILE)
#         print(f"YAML log file {NEW_PROCESS_LOG_FILE} removed.")

# def is_your_script_running(*args, **kwargs):
#     """
#     Check if the script is running by reading PIDs from the YAML log file.
#     """
#     if not os.path.exists(NEW_PROCESS_LOG_FILE):
#         print("No running process found.")
#         return False

#     # Load PIDs from the YAML file
#     with open(NEW_PROCESS_LOG_FILE, "r") as log_file:
#         pids = yaml.safe_load(log_file)

#     for key, pid in pids.items():
#         try:
#             pid = int(pid)
#             process = psutil.Process(pid)
#             if process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
#                 print(f"The process with PID {pid} is running.")
#                 return True
#         except psutil.NoSuchProcess:
#             print(f"No process with PID {pid} found.")
#     return False

# def main(command: str = "start") -> None:
#     """
#     Run the appropriate function based on the command.
#     Args:
#         command: One of 'start', 'stop', or 'info'
#     """
#     os.makedirs(os.path.join(DEFAULT_DIR, 'logs', 'activities'), exist_ok=True)
#     if command == "start":
#         run_your_script_detached()
#         ctypes.windll.user32.MessageBoxW(0, "Monitoring started", "Info", 0)
#     elif command == "stop":
#         stop_your_script()
#     elif command == "info":
#         is_your_script_running()


if __name__ == "__main__":
    alert()
    # main(command="start")
