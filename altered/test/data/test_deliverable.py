import os
import re
from typing import List

def find_matching_files(directory: str, pattern: str) -> List[str]:
    """
    Find all files in the given directory that match the provided regex pattern.

    Args:
        directory (str): The path of the directory to search in.
        pattern (str): The regex pattern to match the file names.

    Returns:
        List[str]: A list of matching file paths.
    """
    matching_files = []
    regex = re.compile(pattern)

    for root, _, files in os.walk(directory):
        for file_name in files:
            if regex.match(file_name):
                matching_files.append(os.path.join(root, file_name))

    return matching_files

# Example usage:
# matching_files = find_matching_files('/path/to/directory', r'^.*\.txt$')
# print(matching_files)  # This will print all .txt files in the directory and subdirectories.
