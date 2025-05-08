import requests
import socket
from typing import Optional

class Devices:
    """
    A class for controlling Tasmota devices (i.e. lamp, tasmota plug) via a custom web host.
    Handles hostname resolution with a static IP fallback.
    """
    # Server Configuration
    server_name = "home"
    server_ip = "192.168.0.5" # <<< SET THIS IP >>>
    base_path = "/tasmota"
    request_timeout = 5

    @classmethod
    def prep_url(cls, full_name: str) -> Optional[str]:
        """
        Prepares the full URL for toggling a device.
        Attempts hostname resolution first, falls back to static IP on failure.
        """
        host = None
        try:
            host = socket.gethostbyname(cls.server_name)
        except socket.gaierror:
            print(f"Warning: Hostname '{cls.server_name}' resolution failed. "
                  f"Using static IP fallback {cls.server_ip}.")
            host = cls.server_ip
        except Exception as e:
             print(f"Warning: Unexpected error resolving '{cls.server_name}': {e}. "
                   f"Using static IP fallback {cls.server_ip}.")
             host = cls.server_ip
        if not host:
            print("Error: Could not determine host address.")
            return None
        url = f"http://{host}{cls.base_path}/toggle?name={full_name}"
        return url

    @classmethod
    def _make_request_and_report(cls, url: str, full_name: str, timeout: int) -> bool:
        """
        Internal helper to make the HTTP request and handle print/error reporting.
        Returns True on success, False on failure.
        """
        print(f"Calling URL: {url}\n")
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            print(f"Success: Device '{full_name}' toggled.")
            return True
        except requests.exceptions.Timeout:
            print(f"Error: Request timed out when trying to toggle '{full_name}'.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with host when toggling '{full_name}': {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred when toggling '{full_name}': {e}")
            return False

    @classmethod
    def toggle_device(cls, *args, room: str, name: str, **kwargs) -> bool:
        """
        Toggles a Tasmota device via the custom host using its name and room.
        Args:
            room (str): The room where the device is located.
                        E.g. 'office', 'living', 'terrasse'.
            name (str): The calling name of the device.
                        E.g. 'panel_led_lamp', 'gold_lamp', 'side_lamp', 'light_strip'.
            *args: Arbitrary positional arguments (ignored).
            **kwargs: Arbitrary keyword arguments (ignored).
        Returns:
            bool: True if the request was successfully made (received 2xx status), 
            False otherwise.
        """
        full_name = f"{name}_{room}"
        print(f"Attempting to toggle device: '{full_name}')")
        # construct url: url = f"http://{host}{cls.base_path}/toggle?name={full_name}"
        url = cls.prep_url(full_name)
        if url is None:
            print("Toggle aborted due to URL preparation failure.")
            return False
        # make request: r = requests.get(url, timeout=cls.request_timeout)
        return cls._make_request_and_report(url, full_name, cls.request_timeout)

