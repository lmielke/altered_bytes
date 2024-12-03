"""
info_git_diff.py
"""

import subprocess
from colorama import Fore, Style, init
import re


class GitDiffs:
    """
    A class to handle extracting and formatting Git diff results.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the class.
        """
        self.changes = []

    def extract_git_diff(self, *args, **kwargs) -> str:
        """
        Extract the raw git diff output using subprocess.

        Returns:
            str: The raw git diff output.
        """
        try:
            # Run git diff to get the changes
            git_diff_cmd = ['git', 'diff']
            result = subprocess.run(git_diff_cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()

        except subprocess.CalledProcessError as e:
            return f"Error retrieving git diff: {e}"

    def parse_git_diff(self, raw_diff:str, *args, num_activities:int, **kwargs) -> None:
        """
        Parse the raw git diff output and store changes in the class list.

        Args:
            raw_diff (str): The raw output from the git diff command.
            num_activities (int): Number of recent changes to extract.
        """
        changes = raw_diff.split('diff --git')

        # Extract the last 'num_activities' blocks and process them
        for change in changes[-num_activities:]:
            change = change.strip()
            if change:
                lines = change.splitlines()

                # Extract the filename from the first line in the block
                if lines:
                    file_line = lines[0]  # The first line contains the file paths
                    file_path = file_line.split()[-1].split('/')[-1]  # Extract filename

                    # Find the starting line and range from the '@@' line
                    start_end_match = re.search(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', change)
                    if start_end_match:
                        start_old = int(start_end_match.group(1))
                        length_old = int(start_end_match.group(2))
                        start_new = int(start_end_match.group(3))
                        length_new = int(start_end_match.group(4))
                        start_ends = [f"{start_old}+{length_old}", f"{start_new}+{length_new}"]
                    else:
                        start_ends = ["unknown", "unknown"]

                    # Collect the content of the change
                    content = '\n'.join(lines)
                    cleaned_content = self.escape_jinja_syntax(content)
                    # Add the change data to the list
                    self.changes.append({
                        'file_path': file_path,
                        'start_ends': start_ends,
                        'content': cleaned_content
                    })


    def escape_jinja_syntax(self, content: str) -> str:
        """
        Escape Jinja-like syntax in git diff content by replacing special characters.

        Args:
            content (str): The raw git diff content.

        Returns:
            str: The escaped git diff content.
        """
        # Replace problematic Jinja-related characters with HTML-safe versions
        content = content.replace('{{', '$').replace('}}', '$')
        content = content.replace('{%', '$').replace('%}', '$')
        return content

    def get_git_diffs(self, *args, **kwargs) -> list:
        """
        Main method to extract and parse the git diffs, then return the results as a list.

        Args:
            num_activities (int): Number of recent changes to extract.

        Returns:
            list: A list containing dictionaries for each parsed git diff.
        """
        # Step 1: Extract raw git diff
        raw_diff = self.extract_git_diff(*args, **kwargs)

        # Step 2: Parse the raw diff and store in the list
        self.parse_git_diff(raw_diff, *args, **kwargs)

        # Step 3: Return the list with parsed changes
        return self.changes


# Example usage
if __name__ == "__main__":
    git_diffs = GitDiffs()  # Instantiate the GitDiffs class
    recent_changes = git_diffs.get_git_diffs(num_activities=2)  # Specify how many changes to track
    print(recent_changes)
