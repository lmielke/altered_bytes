# test_info_os_system.py

import os, platform, re, socket, unittest, yaml
from altered.info_os_system import SysInfo

class Test_SysInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.sys_info = SysInfo()

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        with open(SysInfo.file_path, "r") as f:
            out = yaml.safe_load(f)
        return out

    def test___init__(self, *args, **kwargs):
        self.assertEqual(self.sys_info.os_type, platform.system())

    def test___call__(self, *args, **kwargs):
        system_data = self.sys_info()
        self.assertEqual(
            f"{system_data.get('psversiontable')}",
            f"{self.test_data[socket.gethostname().lower()].get('psversiontable')}"
        )

    def test_get_os_info(self, *args, **kwargs):
        os_info = self.sys_info.get_os_info()
        os_regex = re.compile(r'Windows \d{1,2}, \d{1,2}\.\d{1,5}')
        self.assertRegex(os_info.get('os'), os_regex, f"OS info format incorrect: {os_info}")

    def test_get_cpu_info(self, *args, **kwargs):
        cpu_info = self.sys_info.get_cpu_info()
        self.assertIn('Name', cpu_info, "Missing 'Name' in CPU info")
        self.assertIn('LoadPercentage', cpu_info, "Missing 'LoadPercentage' in CPU info")

        cpu_name_regex = re.compile(r'Intel\(R\)|AMD\s.*CPU')
        self.assertRegex(cpu_info['Name'], cpu_name_regex, f"Unexpected CPU name: {cpu_info['Name']}")

        cpu_load_regex = re.compile(r'\d{1,3}')
        self.assertRegex(cpu_info['LoadPercentage'], cpu_load_regex, f"Unexpected CPU load: {cpu_info['LoadPercentage']}")

    def test_get_ram_info(self, *args, **kwargs):
        ram_info = self.sys_info.get_ram_info()
        ram_regex = re.compile(r'\d{1,2}\.\d{1,2} GB')
        self.assertRegex(ram_info, ram_regex, f"RAM size format incorrect: {ram_info}")

    def test_get_disk_info(self, *args, **kwargs):
        disk_info = self.sys_info.get_disk_info()
        disk_regex = re.compile(r'\d{1,4}\.\d{1,2} GB')
        self.assertRegex(disk_info, disk_regex, f"Disk size format incorrect: {disk_info}")

    def test_get_gpu_info(self, *args, **kwargs):
        gpu_info = self.sys_info.get_gpu_info()
        for gpu_key, gpu_name in gpu_info.items():
            self.assertTrue(gpu_key.startswith('GPU'), f"Unexpected GPU key: {gpu_key}")
            gpu_name_regex = re.compile(r'NVIDIA|Intel|AMD')
            self.assertRegex(gpu_name, gpu_name_regex, f"Unexpected GPU name: {gpu_name}")

    def test_get_network_info(self, *args, **kwargs):
        network_info = self.sys_info.get_network_info()
        self.assertIn('hostname', network_info, "Hostname is missing in network info")
        self.assertIn('ip_address', network_info, "IP address is missing in network info")

        ip_regex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        self.assertRegex(network_info['ip_address'], ip_regex, f"IP address format incorrect: {network_info['ip_address']}")

    def test_get_user_info(self, *args, **kwargs):
        user_info = self.sys_info.get_user_info()
        self.assertTrue(len(user_info) > 0, "Username is empty")

    def test_get_system_info(self, *args, **kwargs):
        system_data = self.sys_info.get_system_info()
        expected_keys = ['os', 'cpu_type', 'ram_size', 'disk_size', 'gpu_info', 'hostname', 'ip_address', 'username']
        
        for key in expected_keys:
            self.assertIn(key, system_data, f"Missing key: {key}")

if __name__ == "__main__":
    unittest.main()