"""
devices.py
C:/Users/lars/python_venvs/packages/altered_bytes/altered/devices.py
"""
import os, re
import requests
import socket
import json
from typing import Optional, Dict, Any

class Devices:
    """
    A class for controlling and querying Tasmota devices via a custom web server.
    Handles server address resolution with fallback and fetches device list from a JSON API endpoint.
    """
    # Server Configuration
    server_hostname = "home"
    server_ip = "192.168.0.5" # <<< SET THIS IP >>>
    base_path = "/tasmota" # Base path of the server endpoint
    request_timeout = 5 # Timeout for all HTTP requests made by this class

    @classmethod
    def prep_url(cls, full_device_name: str) -> Optional[str]:
        """
        Prepares the full URL for toggling a device.
        Attempts hostname resolution first, falls back to static IP on failure.
        """
        server_host = None
        try:
            server_host = socket.gethostbyname(cls.server_hostname)
        except socket.gaierror:
            print(f"Warning: Hostname '{cls.server_hostname}' resolution failed. "
                  f"Using static IP fallback {cls.server_ip}.")
            server_host = cls.server_ip
        except Exception as e:
             print(f"Warning: Unexpected error resolving '{cls.server_hostname}': {e}. "
                   f"Using static IP fallback {cls.server_ip}.")
             server_host = cls.server_ip
        if not server_host:
            print("Error: Could not determine server address.")
            return None
        url = f"http://{server_host}{cls.base_path}/toggle?name={full_device_name}"
        return url

    @classmethod
    def _make_request_and_report(cls, url: str, full_device_name: str, timeout: int) -> bool:
        """
        Internal helper to make the HTTP request and handle print/error reporting.
        Returns True on success, False on failure.
        """
        print(f"Calling URL: {url}")
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            print(f"Success: Device '{full_device_name}' toggled.")
            return True
        except requests.exceptions.Timeout:
            print(f"Error: Request timed out when trying to toggle '{full_device_name}'.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with server when toggling '{full_device_name}': {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred when toggling '{full_device_name}': {e}")
            return False

    @classmethod
    def toggle_device(cls, *args, room: str, name: str, **kwargs) -> bool:
        """
        Toggles a Tasmota device via the custom server using its name and room.

        Args:
            room (str): The room where the device is located.
            name (str): The specific name of the device.
        """
        full_device_name = f"{name}_{room}"
        # REQUEST_TIMEOUT variable removed as cls.request_timeout is used directly
        url = cls.prep_url(full_device_name)
        print(f"Attempting to toggle device: '{full_device_name}'), \nURL: {url}")
        if url is None:
            print("Toggle aborted due to URL preparation failure.")
            return False
        # Delegate the actual request and reporting to the helper method and return its result
        return cls._make_request_and_report(url, full_device_name, cls.request_timeout)


    # --- Modify list_devices to fetch JSON ---
    @classmethod
    def list_devices(cls) -> Dict[str, Dict[str, Any]]:
        """
        Queries the server's JSON device status endpoint to get the list of devices and their states.
        Returns:
            Dict[str, Dict[str, Any]]: A dictionary like {ip: {'title': ..., 'state': ...}, ...}.
                                       Returns an empty dictionary if fetching/parsing fails.
        """
        print(f"Attempting to list devices from server ({cls.server_hostname} or {cls.server_ip})...")
        try:
            # Determine the server host (replicate logic from prep_url)
            server_host = None
            try:
                server_host = socket.gethostbyname(cls.server_hostname)
            except socket.gaierror:
                server_host = cls.server_ip
            except Exception as e:
                 print(f"Warning: Error resolving {cls.server_hostname} for list: {e}. Using {cls.server_ip}.")
                 server_host = cls.server_ip
            if not server_host:
                print("Error: Could not determine server address for list.")
                return {} # Return empty dict on failure
            # Construct the URL for the new JSON status endpoint
            status_url = f"http://{server_host}{cls.base_path}/device_status"
            print(f"Fetching JSON from URL: {status_url}")
            # Make the request
            r = requests.get(status_url, timeout=cls.request_timeout)
            r.raise_for_status() # Check for HTTP errors (e.g., 404 if endpoint is wrong, 500 from server)
            # Parse the JSON response
            devices_data = r.json()
            # Basic validation: Ensure it's a dictionary
            if not isinstance(devices_data, dict):
                 print(f"Error: Received unexpected data format from server ({type(devices_data)}). Expected a dictionary.")
                 # print(f"Response content: {r.text}") # Optional: print response text if parsing fails
                 return {} # Return empty dict if format is wrong
            print(f"Successfully fetched status for {len(devices_data)} devices.")
            return devices_data # Return the parsed dictionary
        except requests.exceptions.Timeout:
            print(f"Error: Request timed out getting list from server.")
            return {}
        except requests.exceptions.RequestException as e:
            # This catches connection errors AND HTTP errors from raise_for_status()
            print(f"Error getting list from server: {e}")
            return {}
        except json.JSONDecodeError:
            # Catch errors if the response is not valid JSON
             print(f"Error: Could not parse JSON response from {status_url}. Is the server running and configured correctly?")
             # print(f"Response content: {r.text}") # Optional: print response text if parsing fails
             return {}
        except Exception as e:
             print(f"An unexpected error occurred while fetching list: {e}")
             return {}

    @classmethod
    def save_to_file(self, *args, category:str, datetime_str:str, **kwargs) -> None:
        """
        Saves the content of a document to a file in the specified directory. The file name
        must derived from the provided file_content i.e. (classification label, datetime_str).
        The goal of this is to categorize files inside a directory based on their content.
        Example: 
        16.06.2025

        Hi friends, lets have a party next weekend.
        cu soon

        Expected file name: invites_2025-06-16.txt, 
                            kwargs = {'category': 'invites', 'datetime': '2025-06-16'}
        Expected tool_call:
                            {'name': 'save_to_file', 
                            'arguments': {'category': 'invites', 'datetime_str': '2025-06-16'}}
        Args:
            category (str): The category or label for the file, used in the file name.
            datetime_str (str): A string representing the date and time, used in the file name.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Allowed categories:
            - invites
            - gas_provider
            - electricity_provider
            - water_provider
            - spam
            - work
            - personal
            - undefined
        """
        # first we load the file_content that we want to save
        # NOTE: this is the same file_content that was given to the LLM for categorization
        file_content = Devices.get_next_file_content(*args, **kwargs)
        # we create the file name and remove any unwanted characters
        file_name = re.sub(r'[\\/*?:"<>|]', '', f"{category}_{datetime_str}.txt")
        # we save the file inside the os.cwd
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(file_content)

    @staticmethod
    def get_next_file_content(*args, file_dir:str=r'C:/temp/file_saver', **kwargs):
        with open(os.path.join(file_dir, 'source_files', 'some_text.txt'), 'r', encoding='utf-8') as file:
            file_content = file.read()
        os.chdir(os.path.join(file_dir, 'target_files'))
        return file_content.strip()

if __name__ == "__main__":
    # Example usage
    devices = Devices.list_devices()
    print(devices)
