"""
prompt_context_activities.py
"""

import json
import os
import glob
from datetime import datetime
from colorama import Fore, Style
from collections import OrderedDict

import altered.settings as sts
from altered.info_os_system import SysInfo

class ContextOsSystem:

    template_name = 'i_context_os_system.md'
    trigger = 'sys_info'

    def __init__(self, *args, **kwargs):
        self.context = {}
        self.sys_info = SysInfo(*args, **kwargs)

    def get_os_info(self, *args, **kwargs) -> dict:
        os_infos = self.sys_info(*args, **kwargs)
        return os_infos

    def mk_context(self, *args, sys_info:bool=False, **kwargs):
        if not sys_info:
            return {}
        self.context = {
            'os_infos': self.get_os_info(*args, **kwargs),
        }
        return self.context
