"""
prompt_deliverable.py
"""

import json
import os
import glob
from datetime import datetime
from colorama import Fore, Style

import altered.settings as sts


class Deliverable:

    template_name = 'i_deliverable.md'
    trigger = 'deliverable'

    def __init__(self, *args, **kwargs):
        self.deliverable = ''
        self.context = {}

    def get_context_info(self, *args, deliverable_path:str=None, **kwargs) -> dict:
        print(f"{Fore.RED}deliverable_path = {deliverable_path}{Fore.RESET}")
        if deliverable_path is not None:
            with open(deliverable_path, 'r') as f:
                self.deliverable = f.read()
        return self.deliverable

    def mk_context(self, *args, deliverable:bool=False, **kwargs):
        if not deliverable: return {}
        d = self.get_context_info(*args, **kwargs)
        if d:
            self.context['content'] = d
        return self.context

