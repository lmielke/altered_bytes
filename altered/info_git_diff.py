"""
info_git_diff.py
"""

import subprocess
import re, os
from colorama import Fore, Style

class GitDiffs:
    """
    A class to handle extracting and formatting Git diff and status results.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the class.
        """
        # Optionally, you might not need to keep self.changes now.
        self.changes = []

    def extract_git_status(self, *args, **kwargs) -> str:
        """
        Extract the raw git status output using subprocess, suppressing the window.
        Returns:
            str: The raw git status output.
        """
        try:
            git_cmd = ['git', 'status', '--porcelain']
            
            # --- For Windows: Prepare to hide the console window ---
            flags = 0
            if os.name == 'nt': # 'nt' is for Windows operating systems
                flags = subprocess.CREATE_NO_WINDOW

            # Specify encoding and error handling
            result = subprocess.run(
                git_cmd,
                capture_output=True,
                text=True,          # Ensures stdout/stderr are strings
                check=True,         # Raises CalledProcessError on non-zero exit codes
                encoding='utf-8',   # Specifies decoding for text=True
                errors='replace',   # Handles decoding errors
                creationflags=flags # Pass the flags to suppress window creation
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            # If text=True, e.stderr should already be a string (or None)
            stderr_output = e.stderr.strip() if e.stderr else ""
            # Your original decode was fine too, but often not needed with text=True for e.stderr
            # stderr_output = e.stderr.decode('utf-8', errors='replace').strip() if e.stderr else "" 
            return f"Error retrieving git status: {e}. Stderr: {stderr_output}"
        except Exception as e: # Catch other potential errors like FileNotFoundError if git isn't installed
            return f"An unexpected error occurred during git status: {e}"

    def parse_git_status(self, raw_status: str, *args, **kwargs) -> dict:
        """
        Parse the raw git status output and build a dictionary of file paths.
        
        Args:
            raw_status (str): The raw output from git status --porcelain.
        
        Returns:
            dict: A dictionary with keys 'modified', 'new', and 'deleted'.
        """
        status_dict = {'modified': [], 'new': [], 'deleted': []}
        for line in raw_status.splitlines():
            if not line.strip():
                continue
            # Split each line into status code and file path.
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            code, file_path = parts[0], parts[1].strip()
            if code == "??" or "A" in code:
                status_dict['new'].append(file_path)
            elif "D" in code:
                status_dict['deleted'].append(file_path)
            else:
                status_dict['modified'].append(file_path)
        return status_dict

    def get_git_status(self, *args, **kwargs) -> dict:
        """
        Get the git status as a dictionary.
        
        Returns:
            dict: The dictionary containing keys 'modified', 'new', and 'deleted'.
        """
        raw_status = self.extract_git_status(*args, **kwargs)
        return self.parse_git_status(raw_status, *args, **kwargs)

    def extract_git_diff(self, *args, **kwargs) -> str:
        """
        Extract the raw git diff output using subprocess, suppressing the window.
        Returns:
            str: The raw git diff output.
        """
        try:
            git_cmd = ['git', 'diff']
            
            # --- For Windows: Prepare to hide the console window ---
            si = None
            flags = 0
            if os.name == 'nt': # 'nt' is for Windows
                # This flag prevents the console window from appearing.
                flags = subprocess.CREATE_NO_WINDOW
                # You can also use startupinfo for more control if needed,
                # but CREATE_NO_WINDOW is often sufficient.
                # si = subprocess.STARTUPINFO()
                # si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                # si.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(
                git_cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace',
                creationflags=flags, # Pass the flags here
                # startupinfo=si # Use if you chose the startupinfo route
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.strip() if isinstance(e.stderr, str) else (e.stderr.decode('utf-8', errors='replace').strip() if e.stderr else "")
            return f"Error retrieving git diff: {e}. Stderr: {stderr_output}"
        except Exception as e:
            return f"An unexpected error occurred during git diff: {e}"


    def parse_git_diff(self, raw_diff: str, num_activities: int,
                       *args, **kwargs) -> list:
        """
        Parse the raw git diff output and return a list of change dictionaries.
        
        Args:
            raw_diff (str): The raw output from the git diff command.
            num_activities (int): Number of recent changes to extract.
        
        Returns:
            list: A list containing dictionaries for each parsed git diff.
        """
        diff_changes = []
        changes = raw_diff.split('diff --git')
        for change in changes[:num_activities + 1]:
            change = change.strip()
            if change:
                lines = change.splitlines()
                if lines:
                    file_line = lines[0]
                    file_path = file_line.split()[-1].split('/')[-1]
                    start_end_match = re.search(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@',
                                                change)
                    if start_end_match:
                        start_old = int(start_end_match.group(1))
                        length_old = int(start_end_match.group(2))
                        start_new = int(start_end_match.group(3))
                        length_new = int(start_end_match.group(4))
                        start_ends = [f"{start_old}+{length_old}",
                                      f"{start_new}+{length_new}"]
                    else:
                        start_ends = ["unknown", "unknown"]
                    content = '\n'.join(lines)
                    cleaned_content = self.escape_jinja_syntax(content)
                    diff_changes.append({
                        'file_path': file_path,
                        'start_ends': start_ends,
                        'content': cleaned_content
                    })
        return diff_changes

    def escape_jinja_syntax(self, content: str) -> str:
        """
        Escape Jinja-like syntax in git diff content by replacing special characters.
        
        Args:
            content (str): The raw git diff content.
        
        Returns:
            str: The escaped git diff content.
        """
        content = content.replace('{{', '$').replace('}}', '$')
        content = content.replace('{%', '$').replace('%}', '$')
        return content

    def get_git_diffs(self, num_activities:int=1, *args, **kwargs) -> list:
        """
        Get the git diffs as a list.
        Args:
            num_activities (int): Number of recent changes to extract.
        Returns:
            list: A list of parsed git diff dictionaries.
        """
        raw_diff = self.extract_git_diff(*args, **kwargs)
        diff_changes = self.parse_git_diff(raw_diff, num_activities, *args, **kwargs)
        if 'Not a git repository' in raw_diff:
            diff_changes.append('Not a git repository')
        return diff_changes


# Example usage
if __name__ == "__main__":
    git_diffs = GitDiffs()

    # Get and print git status separately.
    status = git_diffs.get_git_status()
    print("\nGit Status:")
    print(status)

    # Get and print git diffs separately.
    diffs = git_diffs.get_git_diffs(num_activities=3)
    print("\nGit Diffs:")
    for i, diff in enumerate(diffs):
        print(f"\n{i}: {diff}")
