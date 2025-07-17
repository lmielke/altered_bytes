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
from altered.info_git_diff import GitDiffs

class ContextActivities:

    template_name = 'i_context_user_info.md'
    log_name = 'activity_log'
    trigger = 'user_act'

    def __init__(self, *args, log_file_path:str=None, **kwargs):
        """
        Initialize the class with the path to the most recent activity log file.
        If no specific log_file_path is provided, it will find the most recent log file.
        """
        self.log_file_path = self.find_most_recent_act_log(*args, **kwargs) \
                                                if log_file_path is None else log_file_path
        self.context = {}

    def __call__(self, *args, **kwargs):
        return self.get_all_infos(*args, **kwargs)

    def get_all_infos(self, *args,  git_diff:bool=False, 
                                    user_act:bool=False, 
                                    ps_hist:bool=False,
                                    num_activities:int=1,
        **kwargs):
        data = {}
        if any([user_act, ps_hist, git_diff]) and num_activities == 0:
            num_activities = 1
        if user_act and num_activities >= 1:
            self.load_activities(*args, **kwargs)
            data['user_act'] = self.context['user_act'][-num_activities:]
        if ps_hist and num_activities >= 1:
            self.load_ps_history(*args, **kwargs)
            data['ps_history'] = self.context['ps_history'][-num_activities*2:]
        if git_diff and num_activities >= 1:
            self.load_git_diffs(*args, **kwargs)
            data['git_diffs'] = self.context['git_diffs'][-num_activities:]
        if git_diff and num_activities >= 1:
            self.load_git_status(*args, **kwargs)
            data['git_status'] = self.context['git_status']
        return {'user_info': data}

    def find_most_recent_act_log(self, *args, **kwargs):
        """
        Search the logs directory for the most recent log file based on the timestamp in the filename.
        """
        log_pattern = os.path.join(sts.logs_dir, 'activities', f'*_{self.log_name}.json')
        log_files = glob.glob(log_pattern)
        if not log_files:
            raise FileNotFoundError(f"No log files found in {sts.logs_dir}")
        # Extract the timestamp from each filename and find the most recent
        log_files.sort()
        # Return the path to the most recent log file
        return log_files[-1]

    def load_activities(self, *args, **kwargs):
        """
        Load activity records from the most recent log file into the context dictionary.
        """
        if os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'r') as log_file:
                # Load each activity record and append to the context list
                self.context['user_act'] = [json.loads(line.strip()) for line in log_file]
        else:
            self.context['user_act'] = []

    def get_ps_history_file_path(self, *args, **kwargs) -> str:
        """
        Get the path to the PowerShell history file.

        Returns:
            str: The full path to the PowerShell history file.
        """
        appdata_path = os.getenv('APPDATA')
        if appdata_path:
            history_file_path = os.path.join(appdata_path, 'Microsoft', 'Windows', 
                                    'PowerShell', 'PSReadline', 'ConsoleHost_history.txt')
            if os.path.exists(history_file_path):
                return str(history_file_path)
            else:
                raise FileNotFoundError("PowerShell history file not found.")
        else:
            raise EnvironmentError("APPDATA environment variable not found.")

    def load_ps_history(self, text_len: int = 50, *args, **kwargs) -> None:
        """
        Loads PowerShell history, skips invalid characters, removes duplicates
        (keeping last), and filters out 'clear'.
        """
        path = self.get_ps_history_file_path(*args, **kwargs)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
        # take last `text_len`, drop empty/'clear', then de‑dupe preserving last
        recent = [ln for ln in raw.splitlines()[-text_len:] if ln and ln != 'clear']
        self.context['ps_history'] = list(OrderedDict.fromkeys(recent[::-1]))[::-1]

    def load_git_diffs(self, *args, num_activities: int = 3, **kwargs):
        """
        Load the specified number of recent git diffs and add them to the context.

        Args:
            num_activities (int): The number of recent git changes to load.
        """
        # Load git diffs as a list (which can be sliced later)
        self.context['git_diffs'] = GitDiffs(*args, **kwargs).get_git_diffs(
            num_activities=num_activities, *args, **kwargs)

    def load_git_status(self, *args, num_activities: int = 3, **kwargs):
        """
        Load the specified number of recent git status and add them to the context.

        Args:
            num_activities (int): The number of recent git changes to load.
        """
        # Load git status as a dictionary (remains separate)
        self.context['git_status'] = GitDiffs(*args, **kwargs).get_git_status(*args, **kwargs)
