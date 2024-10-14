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

    template_name = 'i_context_activities.md'
    logs_dir = sts.logs_dir
    log_name = 'activity_log'
    trigger = 'activities'

    def __init__(self, *args, log_file_path:str=None, **kwargs):
        """
        Initialize the class with the path to the most recent activity log file.
        If no specific log_file_path is provided, it will find the most recent log file.
        """
        self.log_file_path = self.find_most_recent_act_log(*args, **kwargs) \
                                                if log_file_path is None else log_file_path
        self.context = {}
        self.load_activities(*args, **kwargs)
        self.load_ps_history(*args, **kwargs)
        self.load_git_diffs(*args, **kwargs)

    def find_most_recent_act_log(self, *args, **kwargs):
        """
        Search the logs directory for the most recent log file based on the timestamp in the filename.
        """
        log_pattern = os.path.join(self.logs_dir, f'*_{self.log_name}.json')
        log_files = glob.glob(log_pattern)
        if not log_files:
            raise FileNotFoundError(f"No log files found in {self.logs_dir}")
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
                self.context['activities'] = [json.loads(line.strip()) for line in log_file]
        else:
            self.context['activities'] = []

    def get_activities_results(self, *args, num_activities:int=0, **kwargs):
        """
        Retrieve the most recent 'num_activities' activities.
        """
        if not num_activities: return {}
        return { 
                'activities': self.context['activities'][-num_activities:],
                'ps_history': self.context['ps_history'][-num_activities*2:],
                'git_diffs': self.context['git_diffs'][-num_activities:],
                }

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

    def load_ps_history(self, text_len:int=50, *args, **kwargs) -> None:
        """
        Loads PowerShell history from a file, removes duplicates (keeping the last occurrence)
        and the 'clear' term, and stores it in the context.

        Args:
            text_len: (int) Number of recent lines to retrieve from the history.
        """
        with open(self.get_ps_history_file_path(*args, **kwargs), 'r') as f:
            # Read the lines and get the last 'text_len' lines, filtering out empty lines and 'clear'
            lines = [l for l in f.read().split('\n')[-text_len:] if l and l != 'clear']
            # Reverse the list back to the original order with last occurrences preserved
            self.context['ps_history'] = list(OrderedDict.fromkeys(lines[::-1]))[::-1]

    def load_git_diffs(self, *args, num_activities:int=3, **kwargs):
        """
        Load the specified number of recent git diffs and add them to self.context['git_diffs'].

        Args:
            num_changes (int): The number of recent git changes to load.
        """
        # Initialize the GitDiffs class with the number of changes
        git_diffs = GitDiffs(*args, **kwargs)

        # Get the recent git diffs in a structured dictionary
        diffs = git_diffs.get_git_diffs(*args, num_activities=num_activities, **kwargs)
        # Add the parsed git diffs to the context dictionary
        self.context['git_diffs'] = diffs