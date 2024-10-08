"""
prompt_context_activities.py
"""

import json
import os
import glob
from datetime import datetime
import altered.settings as sts

class ContextActivities:

    template_name = 'i_context_activities.md'
    logs_dir = sts.logs_dir
    log_name = 'activity_log'

    def __init__(self, *args, log_file_path:str=None, **kwargs):
        """
        Initialize the class with the path to the most recent activity log file.
        If no specific log_file_path is provided, it will find the most recent log file.
        """
        self.log_file_path = self.find_most_recent_log(*args, **kwargs) \
                                                if log_file_path is None else log_file_path
        self.context = {}
        self.load_activities(*args, **kwargs)
        self.load_ps_history(*args, **kwargs)

    def find_most_recent_log(self, *args, **kwargs):
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

    def get_activities_results(self, *args, num_activities:int=5, **kwargs):
        """
        Retrieve the most recent 'num_activities' activities.
        """
        activities = [a for a in self.context['ps_history'][-num_activities*3:] if a]
        return { 
                'activities': self.context['activities'][-num_activities:],
                'ps_history': activities[-num_activities*2:],
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

    def load_ps_history(self, text_len:int=100, *args, **kwargs):
        with open(self.get_ps_history_file_path(*args, **kwargs), 'r') as f:
            self.context['ps_history'] = f.read().split('\n')[-text_len:]
