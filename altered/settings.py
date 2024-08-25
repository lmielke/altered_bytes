# settings.py
import os, re, sys, time, yaml
from datetime import datetime as dt

package_name = "altered"
package_dir = os.path.dirname(__file__)
project_dir = os.path.dirname(package_dir)
project_name = os.path.basename(project_dir)

apis_dir = os.path.join(package_dir, "apis")
apis_json_dir = os.path.join(package_dir, "apis", "json_schemas")
chat_logs_dir = os.path.join(package_dir, 'gp', 'chat_logs')
resources_dir = os.path.join(package_dir, "resources")
instructions_file = lambda expert: os.path.join(resources_dir, f"Readme_{expert}.md")

test_dir = os.path.join(package_dir, "test")
test_data_dir = os.path.join(test_dir, "data")

# color settings
import colorama
# colors to be used everywhere
YELLOW = colorama.Fore.YELLOW
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
MAGENTA = colorama.Fore.MAGENTA
BLUE = colorama.Fore.BLUE
CYAN = colorama.Fore.CYAN
WHITE = colorama.Fore.WHITE
# additional color options
DIM = colorama.Style.DIM
# setting back to normal
RESET = colorama.Fore.RESET
ST_RESET = colorama.Style.RESET_ALL

colors = {
            'YELLOW': YELLOW,
            'GREEN': GREEN,
            'MAGENTA': MAGENTA,
            'BLUE': BLUE,
            'CYAN': CYAN,
            'WHITE': WHITE,
            'RED': RED,
         }
colors_in_use = {}
default_color, sudo_color, user_color = 'RED', 'RED', 'YELLOW'
sudo_color_code, user_color_code = RED, YELLOW
colors_available = set(colors.keys())
# RED is reserved for sudo, so can not be used by any other expert
colors_available.remove(sudo_color.upper())
colors_available.remove(user_color.upper())
# content formatting
code_color = BLUE
language_color = CYAN
# expert settings
experts, in_chat = {}, set()
# due to available colors, the number of experts is limited to 7
max_experts = len(colors_available)

# openaiFunction = '@OpenAi.function'.lower()
open_ai_func_prefix = 'open_ai_api_'
json_ext = '.json'

time_stamp = lambda: re.sub(r"([: .])", r"-" , str(dt.now()))
session_time_stamp = time_stamp()

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
tags = {
            "general": ["<general_info>", "</general_info>"],
            "instructs": ["<instructions>", "</instructions>", CYAN],
            "package": ["<package_info>", "</package_info>"],
            "system": ["<system_info>", "</system_info>"],
            "project": ["<project_info>", "</project_info>"],
            "network": ["<network_info>", "</network_info>"],
            "python": ["<python_info>", "</python_info>"],
            "docker": ["<docker_info>", "</docker_info>"],
            "unittest": ["<unittest_info>", "</unittest_info>"],
}

roles = {'assistant': MAGENTA, 'user': GREEN, 'system': YELLOW, 'unittest': CYAN, }
# experts = {'sherlock': CYAN, 'moe': YELLOW, 'mr_robot': BLUE, 'you': GREEN, 
            # 'alice': BLUE, 'bob': CYAN}
watermark = f"{YELLOW}►{RESET}"
# instructions
readme_dir = os.path.join(package_dir, 'gp', 'readmes')
instruct_path = lambda expert_name: os.path.join(readme_dir, f"{expert_name}.md")

# Task settings
assembly_ixs = {0: 'low', 1: 'medium', 2: 'moderate', 4: 'high',}
skills = {
            'sudo': ['network', 'system', 'project', 'docker', 'python'], 
            'system': ['network', 'system'], 
            'programmer': ['python'], 
            'architect': ['project', 'docker']
            }

default_config_path = os.path.join(resources_dir, 'models', 'models_servers.yml')


models_config_path = os.path.join(resources_dir, 'models/models_servers.yml')