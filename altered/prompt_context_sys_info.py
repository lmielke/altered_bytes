"""
prompt_context_sys_info.py
"""

import json
import os
import glob
from datetime import datetime
from colorama import Fore, Style
from collections import OrderedDict

import altered.settings as sts
from altered.info_sys_info import SysInfo


class ContextSysInfo:

    template_name = 'i_context_sys_info.md'
    trigger = 'sys_info'

    def __init__(self, *args, **kwargs):
        self.context = {}
        self.sys_info = SysInfo(*args, **kwargs)

    def get_context_info(self, *args, **kwargs) -> dict:
        sys_info = self.sys_info(*args, **kwargs)
        return sys_info

    def mk_context(self, *args, sys_info_ops:bool=False, sys_info_usr:bool=False, **kwargs):
        if not (sys_info_ops or sys_info_usr):
            return {}
        self.context = {self.trigger: self.get_context_info(*args, **kwargs), }
        if sys_info_usr:
            self.context[self.trigger]['sys_info_ops'] = True
        if sys_info_ops:
            self.context[self.trigger]['sys_info_usr'] = True
        return self.context
