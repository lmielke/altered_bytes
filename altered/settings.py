"""
settings.py
use like: 
    import altered.settings as sts
"""
import altered.logs_timeit as logs_timeit
from altered.logs_events import init_event_logger, logprint
import os, re, sys, time, yaml
from datetime import datetime as dt


package_name = "altered"
package_dir = os.path.dirname(__file__)
project_dir = os.path.dirname(package_dir)
project_name = os.path.basename(project_dir)

resources_dir = os.path.join(package_dir, "resources")
templates_dir = os.path.join(resources_dir, "templates")

strats_dir_name = "strats"
strats_dir = os.path.join(resources_dir, strats_dir_name)
io_dir_name = "io"
io_dir = os.path.join(resources_dir, io_dir_name)

kwargs_defaults_dir = os.path.join(resources_dir, "kwargs_defaults")

test_dir = os.path.join(package_dir, "test")
test_data_dir = os.path.join(test_dir, "data")

logs_dir = os.path.join(resources_dir, "logs")

apis_json_dir = os.path.join(resources_dir, "apis_json")
open_ai_func_prefix = "openai"

### setup runtime measures ###
time_strf = "%Y-%m-%d_%H-%M-%S-%f"
time_stamp = lambda: dt.now().strftime(time_strf)
run_time_start = time_stamp()
timer_logs_name = f"{time_stamp()}_timer.log"
timer_logs_path = os.path.join(logs_dir, 'statistics', 'performance')
# Initialize logs_timeit logging with your settings.
logs_timeit.init_timer(timer_logs_path, timer_logs_name)
# Assume logs_dir and time_strf are already defined.
time_stamp = lambda: dt.now().strftime(time_strf)
event_logs_name = f"{time_stamp()}_events.log"
event_logs_path = os.path.join(logs_dir, 'events')

# Initialize the event logger.
init_event_logger(event_logs_path, event_logs_name)

# name of table data when stored to disk
data_dir = os.path.join(resources_dir, "data")
max_files, data_file_exts = 100, {'csv', 'npy'}
time_stamp_regex = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"
data_regex = rf"^{time_stamp_regex}\.[a-z]{3,4}$"

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

table_max_chars = 70

# # Task settings
# assembly_ixs = {0: 'low', 1: 'medium', 2: 'moderate', 4: 'high',}

# default_config_path = os.path.join(resources_dir, 'models', 'models_servers.yml')
models_config_path = os.path.join(resources_dir, 'models/models_servers.yml')


# # server params
repeats = {'num': 1, 'agg': None}

# global_max_token_len = 15_000