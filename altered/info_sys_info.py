"""
info_sys_info.py
"""
import os
import platform
import psutil
import subprocess
import re
import socket
import yaml
import concurrent.futures
from typing import Dict, Any, List # Added List for type hinting
# from colorama import Fore, Style # Not used in this file directly for console output by SysInfo
import altered.settings as sts

# --- Silent Subprocess Helper ---
def run_silent_subprocess(cmd_args: List[str] | str, # Command can be list or string (for shell=True)
                          capture_output: bool = True,
                          text: bool = True,
                          check: bool = False, # Default to False like run, check_output will set it to True
                          shell: bool = False,
                          encoding: str = 'utf-8',
                          errors: str = 'replace',
                          **kwargs) -> subprocess.CompletedProcess:
    """
    Runs a subprocess, suppressing console window creation on Windows.
    Mimics subprocess.run().
    """
    flags = 0
    if os.name == 'nt':  # For Windows
        flags = subprocess.CREATE_NO_WINDOW

    # Ensure creationflags is in kwargs, respecting user-passed one if any,
    # though this function's intent is to add CREATE_NO_WINDOW.
    # For simplicity, we'll just set it.
    final_kwargs = kwargs.copy()
    final_kwargs['creationflags'] = flags

    return subprocess.run(
        cmd_args,
        capture_output=capture_output,
        text=text,
        check=check,
        shell=shell,
        encoding=encoding,
        errors=errors,
        **final_kwargs
    )

def check_output_silent(cmd_args: List[str] | str, shell: bool = False, **kwargs) -> str:
    """
    Mimics subprocess.check_output, but runs silently on Windows.
    Returns stdout.
    """
    # check_output implies capture_output=True and check=True
    process = run_silent_subprocess(
        cmd_args,
        capture_output=True,
        check=True,
        shell=shell,
        **kwargs # Passes encoding, errors, text etc.
    )
    return process.stdout

def getoutput_silent(cmd_string: str, **kwargs) -> str:
    """
    Mimics subprocess.getoutput, but runs silently on Windows.
    Returns combined stdout and stderr.
    """
    # getoutput implies shell=True, text=True, capture_output=True, check=False,
    # and stderr=subprocess.STDOUT
    kwargs.pop('check', None) # Ensure check is False
    kwargs.pop('stderr', None) # Ensure we control stderr

    process = run_silent_subprocess(
        cmd_string,
        capture_output=True,
        text=True, # getoutput uses text mode
        check=False, # getoutput does not raise on error
        shell=True,  # getoutput always uses a shell
        stderr=subprocess.STDOUT,
        **kwargs
    )
    return process.stdout
# --- End Silent Subprocess Helper ---


class SysInfo:
    file_path = os.path.join(sts.resources_dir, 'models', 'models_clients.yml')

    def __init__(self, *args, **kwargs):
        self.os_type = platform.system()

    def __call__(self, *args, **kwargs):
        return self.load_data(*args, **kwargs)

    def load_data(self, *args, **kwargs):
        sys_info = self.get_system_info(*args, **kwargs)
        # It's safer to check if hostname exists and handle case where it might not be in YAML
        hostname_lower = sys_info.get('hostname', '').lower()
        models_clients_for_host = {}
        if hostname_lower:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f: # Added encoding
                    all_models_clients = yaml.safe_load(f)
                    if isinstance(all_models_clients, dict):
                        models_clients_for_host = all_models_clients.get(hostname_lower, {})
            except FileNotFoundError:
                # Optionally log this error
                print(f"Warning: Models clients file not found at {self.file_path}") # Or use logging
            except yaml.YAMLError:
                # Optionally log this error
                print(f"Warning: Error parsing YAML file at {self.file_path}") # Or use logging

        sys_info.update(models_clients_for_host)
        return sys_info

    def get_os_info(self, *args, **kwargs) -> dict:
        os_type = platform.system()
        os_version = platform.version()
        os_release = platform.release()
        return {"os": f"{os_type} {os_release}, {os_version}"}

    def get_cpu_info(self, *args, **kwargs) -> dict:
        cpu_info = {}
        if self.os_type == "Windows":
            try:
                output = check_output_silent(
                    ["powershell", "-NoProfile", "-Command", # Added -NoProfile
                     "Get-CimInstance -ClassName Win32_Processor | Select-Object Name, LoadPercentage"]
                    # universal_newlines=True is equivalent to text=True, handled by helper
                )
                lines = output.strip().splitlines()
                if len(lines) > 2:
                    cpu_data = re.split(r'\s{2,}', lines[2].strip())
                    cpu_name = cpu_data[0].strip()
                    cpu_load = cpu_data[1].strip() if len(cpu_data) > 1 else "Unknown"
                    cpu_info["Name"] = cpu_name
                    cpu_info["LoadPercentage"] = cpu_load
                else:
                    cpu_info["Name"] = "Unknown"
                    cpu_info["LoadPercentage"] = "Unknown"
            except Exception as e:
                cpu_info["Error"] = f"Error fetching CPU info (Win): {str(e)}"
        elif self.os_type == "Linux":
            try:
                output = check_output_silent("lscpu", shell=True)
                # A more robust parsing for lscpu would be needed here,
                # as 'lscpu' provides a lot of info. Example:
                model_name_line = next((line for line in output.splitlines() if "Model name:" in line), None)
                if model_name_line:
                    cpu_info["Name"] = model_name_line.split("Model name:")[1].strip()
                else:
                    cpu_info["Name"] = "Unknown (Linux)"
                # CPU load on Linux is more complex, often read from /proc/stat or using psutil.cpu_percent()
                cpu_info["LoadPercentage"] = f"{psutil.cpu_percent(interval=0.1)}%" # Get current load
            except Exception as e:
                cpu_info["Error"] = f"Error fetching CPU info (Linux): {str(e)}"
        return cpu_info

    def get_ram_info(self, *args, **kwargs) -> str: # Original was get_ram_info returning string
        ram_info = psutil.virtual_memory()
        return f"{round(ram_info.total / (1024 ** 3), 2)} GB"

    # Original code had two get_disk_info methods. I'll keep the more detailed one.
    # The one using psutil.disk_usage('/') was simpler and would be for root disk only.
    def get_disk_info(self, *args, **kwargs) -> dict:
        disk_info_dict = {} # Renamed from disk_info to avoid conflict if you uncomment below
        if self.os_type == "Windows":
            try:
                output = check_output_silent(
                    ["powershell", "-NoProfile", "-Command", # Added -NoProfile
                     "Get-CimInstance -ClassName Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace"]
                )
                lines = output.strip().splitlines()
                if len(lines) > 2:
                    for line in lines[2:]:
                        disk_data = re.split(r'\s+', line.strip())
                        if len(disk_data) >= 1: # DeviceID must be there
                            drive_letter = disk_data[0].strip()
                            total_size_gb, free_space_gb = "N/A", "N/A"
                            try: # Size and FreeSpace might be missing or not numbers
                                if len(disk_data) >= 2 and disk_data[1]:
                                    total_size_gb = round(int(disk_data[1]) / (1024 ** 3), 2)
                                if len(disk_data) >= 3 and disk_data[2]:
                                    free_space_gb = round(int(disk_data[2]) / (1024 ** 3), 2)
                            except ValueError:
                                pass # Keep N/A if conversion fails
                            disk_info_dict[drive_letter] = {
                                "TotalSizeGB": total_size_gb,
                                "FreeSpaceGB": free_space_gb
                            }
            except Exception as e:
                disk_info_dict["Error"] = f"Error fetching disk info (Win): {str(e)}"
        elif self.os_type == "Linux":
            try:
                output = check_output_silent("df -B1 --output=target,size,avail", shell=True) # -B1 for bytes
                lines = output.strip().splitlines()
                if len(lines) > 1:
                    for line in lines[1:]:
                        disk_data = re.split(r'\s+', line.strip()) # df output can have variable spaces
                        if len(disk_data) == 3: # Expecting Mountpoint, Size, Avail
                            mount_point, total_size_str, free_space_str = disk_data
                            disk_info_dict[mount_point.strip()] = {
                                "TotalSizeGB": round(int(total_size_str) / (1024 ** 3), 2),
                                "FreeSpaceGB": round(int(free_space_str) / (1024 ** 3), 2)
                            }
            except Exception as e:
                disk_info_dict["Error"] = f"Error fetching disk info (Linux): {str(e)}"
        return disk_info_dict


    def get_gpu_info(self, *args, **kwargs) -> dict:
        gpus = {}
        if self.os_type == "Windows":
            try:
                output = check_output_silent(
                    ["powershell", "-NoProfile", "-Command", # Added -NoProfile
                     "Get-CimInstance -Namespace root/cimv2 -ClassName Win32_VideoController | Select-Object -ExpandProperty Name"]
                )
                lines = output.strip().splitlines()
                for idx, line in enumerate(lines, start=1):
                    gpu_name = line.strip()
                    gpus[f"GPU{idx}"] = gpu_name if gpu_name else "Unknown"
            except Exception as e:
                gpus["Error"] = f"Error fetching GPU info (Win): {str(e)}"
        elif self.os_type == "Linux":
            try:
                output = check_output_silent("lspci | grep -i VGA", shell=True) # grep -i for case-insensitivity
                # lspci output for GPU can be detailed, this just gets the line(s)
                gpu_lines = output.strip().splitlines()
                for idx, line in enumerate(gpu_lines, start=1):
                    # Attempt to extract a cleaner name
                    match = re.search(r':\s*(.*)\s*\(rev', line)
                    gpu_name = match.group(1) if match else line.strip()
                    gpus[f"GPU{idx}"] = gpu_name
                if not gpu_lines:
                    gpus["Info"] = "No VGA devices found by lspci or grep failed"
            except Exception as e:
                gpus["Error"] = f"Error fetching GPU info (Linux): {str(e)}"
        return gpus

    def get_network_info(self, *args, **kwargs) -> dict:
        hostname = "Unknown"
        ip_address = "Unknown"
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror: # getaddrinfo error
            pass # Keep unknown
        return {
            "hostname": hostname,
            "ip_address": ip_address
        }

    def get_user_info(self, *args, **kwargs) -> str:
        try:
            if self.os_type == "Windows":
                return getoutput_silent("echo %username%").strip()
            elif self.os_type == "Linux":
                return getoutput_silent("whoami").strip()
        except Exception as e:
            return f"Error fetching user info: {str(e)}"
        return "Unknown User"

    # In your info_sys_info.py, inside the SysInfo class:
    def get_system_info(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Retrieve system information in parallel.
        Returns:
            Dict[str, Any]: A dictionary containing various system information.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
            future_os = executor.submit(self.get_os_info)
            future_cpu = executor.submit(self.get_cpu_info)
            future_ram = executor.submit(self.get_ram_info)
            future_disk = executor.submit(self.get_disk_info) # Using the more detailed disk_info
            future_gpu = executor.submit(self.get_gpu_info)
            future_network = executor.submit(self.get_network_info)
            future_user = executor.submit(self.get_user_info)
        final_sys_info = {}
        try:
            # **future_os.result() will merge the dictionary from get_os_info directly
            # e.g., {'os': 'Windows 10...'}
            final_sys_info.update(future_os.result())
        except Exception as e:
            final_sys_info['os_error'] = str(e)
        
        try:
            # Reverting to 'cpu_type' as the key for the CPU information dictionary
            final_sys_info['cpu_type'] = future_cpu.result()
        except Exception as e:
            final_sys_info['cpu_error'] = str(e)
        
        try:
            final_sys_info['ram_size'] = future_ram.result()
        except Exception as e:
            final_sys_info['ram_error'] = str(e)
        
        try:
            # Reverting to 'disk_info' as the key for the disk information dictionary
            final_sys_info['disk_info'] = future_disk.result()
        except Exception as e:
            final_sys_info['disk_error'] = str(e)
        
        try:
            # Reverting to 'gpu_info' as the key for the GPU information dictionary
            final_sys_info['gpu_info'] = future_gpu.result()
        except Exception as e:
            final_sys_info['gpu_error'] = str(e)
        
        try:
            # **future_network.result() will merge the dictionary from get_network_info directly
            # e.g., {'hostname': '...', 'ip_address': '...'}
            final_sys_info.update(future_network.result())
        except Exception as e:
            final_sys_info['network_error'] = str(e)
        
        try:
            final_sys_info['username'] = future_user.result()
        except Exception as e:
            final_sys_info['user_error'] = str(e)
        return final_sys_info

# Example usage
if __name__ == "__main__":
    sys_info_collector = SysInfo() # Renamed from sys_info to avoid conflict
    system_data = sys_info_collector.get_system_info()
    # Pretty print using yaml dump for readability or json for machine readability
    # print(yaml.dump(system_data, indent=2, sort_keys=False))
    for key, value in system_data.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")