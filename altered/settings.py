# settings.py
import os, re, sys, time, yaml
from datetime import datetime as dt

package_name = "altered"
package_dir = os.path.dirname(__file__)
project_dir = os.path.dirname(package_dir)
project_name = os.path.basename(project_dir)

resources_dir = os.path.join(package_dir, "resources")
# max number of files to store in the data directory before being deleted
templates_dir = os.path.join(resources_dir, "templates")

test_dir = os.path.join(package_dir, "test")
test_data_dir = os.path.join(test_dir, "data")

time_strf = "%Y-%m-%d_%H-%M-%S-%f"
time_stamp = lambda: dt.now().strftime(time_strf)
# name of table data when stored to disk
data_dir = os.path.join(resources_dir, "data")
max_files, data_file_exts = 100, {'csv', 'npy'}
data_regex = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.[a-z]{3,4}$"

ignore_dirs = {
                ".git",
                "build",
                "gp",
                "dist",
                "models",
                "*.egg-info",
                "__pycache__",
                ".pytest_cache",    
                ".tox",
}
abrev_dirs = {
                "log",
                "logs",
                "testopia_logs",
                "chat_logs",
}

table_max_chars = 80

# Task settings
assembly_ixs = {0: 'low', 1: 'medium', 2: 'moderate', 4: 'high',}

default_config_path = os.path.join(resources_dir, 'models', 'models_servers.yml')
models_config_path = os.path.join(resources_dir, 'models/models_servers.yml')
