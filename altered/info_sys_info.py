"""
info_sys_info.py
"""
import os, platform, psutil, subprocess, re, socket, yaml
import concurrent.futures
from typing import Dict, Any
from colorama import Fore, Style
import altered.settings as sts


class SysInfo:

    file_path = os.path.join(sts.resources_dir, 'models', 'models_clients.yml')

    def __init__(self, *args, **kwargs):
        self.os_type = platform.system()

    def __call__(self, *args, **kwargs):
        return self.load_data(*args, **kwargs)

    def load_data(self, *args, **kwargs):
        sys_info = self.get_system_info(*args, **kwargs)
        with open(self.file_path, 'r') as f:
            models_clients = yaml.safe_load(f).get(sys_info['hostname'].lower())
        sys_info.update(models_clients)
        return sys_info

    def get_os_info(self, *args, **kwargs) -> dict:
        """
        Retrieves the OS type and version in a single line formatted as:
        'OS: Windows 10, 10.0.19045'
        """
        os_type = platform.system()
        os_version = platform.version()
        os_release = platform.release()

        # Return as a dictionary with formatted OS string
        return {"os": f"{os_type} {os_release}, {os_version}"}

    def get_cpu_info(self, *args, **kwargs) -> dict:
        """
        Retrieves the CPU name and load percentage on Windows using PowerShell Get-CimInstance.
        Returns a dictionary with the CPU name and load percentage.
        """
        cpu_info = {}

        if self.os_type == "Windows":
            try:
                # Using PowerShell to get CPU name and load percentage
                output = subprocess.check_output(
                    ["powershell", "-Command", 
                     "Get-CimInstance -ClassName Win32_Processor | Select-Object Name, LoadPercentage"],
                    universal_newlines=True
                )

                lines = output.strip().splitlines()

                # Skip the header and split the CPU name and load percentage correctly
                if len(lines) > 2:
                    cpu_data = re.split(r'\s{2,}', lines[2].strip())  # Split by two or more spaces
                    cpu_name = cpu_data[0].strip()
                    cpu_load = cpu_data[1].strip() if len(cpu_data) > 1 else "Unknown"

                    cpu_info["Name"] = cpu_name
                    cpu_info["LoadPercentage"] = cpu_load
                else:
                    cpu_info["Name"] = "Unknown"
                    cpu_info["LoadPercentage"] = "Unknown"

            except Exception as e:
                cpu_info["Error"] = f"Error fetching CPU info: {str(e)}"

        elif self.os_type == "Linux":
            try:
                output = subprocess.check_output("lscpu", shell=True, universal_newlines=True)
                cpu_info["Name"] = output.strip()
            except subprocess.CalledProcessError:
                cpu_info["Error"] = "Error fetching CPU info on Linux"

        return cpu_info

    def get_ram_info(self, *args, **kwargs) -> str:
        ram_info = psutil.virtual_memory()
        return f"{round(ram_info.total / (1024 ** 3), 2)} GB"

    def get_disk_info(self, *args, **kwargs) -> str:
        disk_info = psutil.disk_usage('/')
        return f"{round(disk_info.total / (1024 ** 3), 2)} GB"

    def get_gpu_info(self, *args, **kwargs) -> dict:
        """
        Retrieves the names of all video controllers (GPUs) on Windows using PowerShell Get-CimInstance.
        Returns a dictionary with keys 'GPU1', 'GPU2', etc.
        """
        gpus = {}
        
        if self.os_type == "Windows":
            try:
                # Using powershell.exe with forward slashes in the command
                output = subprocess.check_output(
                    ["powershell", "-Command", 
                     "Get-CimInstance -Namespace root/cimv2 -ClassName Win32_VideoController | Select-Object -ExpandProperty Name"],
                    universal_newlines=True
                )
                
                # Clean the output and split lines
                lines = output.strip().splitlines()
                
                # Process and append GPU names as GPU1, GPU2, etc.
                for idx, line in enumerate(lines, start=1):
                    gpu_name = line.strip()
                    gpus[f"GPU{idx}"] = gpu_name if gpu_name else "Unknown"
                
            except Exception as e:
                gpus["Error"] = f"Error fetching GPU info: {str(e)}"
        
        elif self.os_type == "Linux":
            try:
                output = subprocess.check_output("lspci | grep VGA", shell=True, universal_newlines=True)
                gpus["GPU1"] = output.strip()
            except subprocess.CalledProcessError:
                gpus["Error"] = "No GPU found or command failed"

        return gpus


    def get_network_info(self, *args, **kwargs) -> dict:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return {
            "hostname": hostname,
            "ip_address": ip_address
        }

    def get_user_info(self, *args, **kwargs) -> str:
        if self.os_type == "Windows":
            return subprocess.getoutput("echo %username%").strip()
        elif self.os_type == "Linux":
            return subprocess.getoutput("whoami").strip()
        return "Unknown User"

    def get_system_info(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Retrieve system information in parallel.

        Returns:
            Dict[str, Any]: A dictionary containing various system information.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_os = executor.submit(self.get_os_info)
            future_cpu = executor.submit(self.get_cpu_info)
            future_ram = executor.submit(self.get_ram_info)
            future_disk = executor.submit(self.get_disk_info)
            future_gpu = executor.submit(self.get_gpu_info)
            future_network = executor.submit(self.get_network_info)
            future_user = executor.submit(self.get_user_info)

            # Wait for all futures to complete
            concurrent.futures.wait([future_os, future_cpu, future_ram, future_disk, future_gpu, future_network, future_user])

        # Combine results
        system_info = {
            **future_os.result(),
            "cpu_type": future_cpu.result(),
            "ram_size": future_ram.result(),
            "disk_info": future_disk.result(),
            "gpu_info": future_gpu.result(),
            **future_network.result(),
            "username": future_user.result()
        }

        return system_info

    
    def get_disk_info(self, *args, **kwargs) -> dict:
        """
        Retrieves information about all logical disks, including total size and free space.
        Returns a dictionary where keys are the drive letters or mount points.
        """
        disk_info = {}

        if self.os_type == "Windows":
            try:
                # Using PowerShell to get disk information
                output = subprocess.check_output(
                    ["powershell", "-Command",
                     "Get-CimInstance -ClassName Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace"],
                    universal_newlines=True
                )
                lines = output.strip().splitlines()

                if len(lines) > 2:
                    # Skip the header and parse each line
                    for line in lines[2:]:
                        disk_data = re.split(r'\s+', line.strip())  # Split by whitespace
                        if len(disk_data) >= 2:
                            drive_letter = disk_data[0].strip()
                            if len(disk_data) == 3:
                                total_size = int(disk_data[1])
                                free_space = int(disk_data[2])
                            else:
                                total_size = int(disk_data[1])
                                free_space = None  # If free space is not provided, set to 0

                            disk_info[drive_letter] = {
                                "TotalSizeGB": round(total_size / (1024 ** 3), 2),
                                "FreeSpaceGB": round(free_space / (1024 ** 3), 2)
                            }
            except Exception as e:
                disk_info["Error"] = f"Error fetching disk info: {str(e)}"

        elif self.os_type == "Linux":
            try:
                # Using df command to get disk information
                output = subprocess.check_output("df -h --output=target,size,avail", shell=True, universal_newlines=True)
                lines = output.strip().splitlines()

                if len(lines) > 1:
                    # Skip the header and parse each line
                    for line in lines[1:]:
                        disk_data = re.split(r'\s{2,}', line.strip())  # Split by two or more spaces
                        if len(disk_data) >= 3:
                            mount_point = disk_data[0].strip()
                            total_size = disk_data[1].strip()
                            free_space = disk_data[2].strip()

                            disk_info[mount_point] = {
                                "TotalSize": total_size,
                                "FreeSpace": free_space
                            }
            except subprocess.CalledProcessError:
                disk_info["Error"] = "Error fetching disk info on Linux"

        return disk_info

        

# Example usage
if __name__ == "__main__":
    sys_info = SysInfo()
    system_data = sys_info.get_system_info()
    for key, value in system_data.items():
        print(f"{key}: {value}")