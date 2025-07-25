import os
import re
from typing import Set

from colorama import Fore, Style, Back

try:
    import altered.settings as sts
except ImportError:
    global sts
    sts = type('sts', (), {})  # Create a dummy 'sts' object for demonstration
    sts.project_dir = os.getcwd()  # Set project_dir to current working directory


class Tree:
    default_ignores = {'.git', 'altered.egg-info', 'build', '__pycache__', 'logs'}
    default_ignore_files = {r'.*\.sublime-\w*',}
    file_types = {'.py': 'Python', '.yml': 'YAML', '.md': 'Markdown', '.txt': 'Text'}

    def __init__(self, *args, style=None, ignores:list=None, **kwargs):
        """
        Initialize the Tree object with custom symbols and optional file matching regex.

        Args:
            style (str): Style of the tree (not used in this version).
            ignores (list): List of directories to ignore during traversal.
            file_match_regex (str): Regex pattern to match files while traversing.
        """
        self.indent = "    "
        self.ignores = set(ignores) if ignores is not None else self.default_ignores
        self.matched_files: Set[str] = set()
        self.disc_sym = "    | ..."  # Symbol indicating skipped directories

    def handle_ignoreds(self, subdir: str, dirs: list, indent_level: str) -> str:
        """
        Handles ignored directories by adding them to the tree but not traversing into them.

        Args:
            subdir (str): The name of the current directory.
            dirs (list): The list of subdirectories to traverse.
            indent_level (str): The level of indentation for the current directory.

        Returns:
            str: The portion of the tree string that handles ignored directories.
        """
        if any(subdir == ig_dir or subdir.endswith(ig_dir.lstrip("*")) \
                                                                for ig_dir in self.ignores):
            dirs[:] = []  # Stop traversing this directory but indicate more content
            return f"{indent_level}|-- {subdir}/\n{indent_level}{self.disc_sym}\n"
        return ""

    def find_match(self, root: str, file: str, file_match_regex:str, *args, **kwargs):
        """
        Check if a file matches the provided regex and, if so, add it to matched files.

        Args:
            root (str): The path to the current directory.
            file (str): The name of the file to check.
        """
        if file_match_regex and re.search(file_match_regex, file):
            self.matched_files.add(os.path.join(root, file))

    def mk_tree(self, *args, 
                            project_dir:str=None,
                            work_project_dir:str=None,
                            max_depth:int=2, 
                            file_match_regex:str=None,
                            work_file_name:str=None,
        **kwargs) -> str:
        """
        Generate an uncolorized string representation of the directory tree and collect
        matched files.

        Args:
            project_dir (str): The path to the project directory.
            max_depth (int): The maximum depth for directory traversal (None for unlimited).

        Returns:
            str: A string representing the uncolorized directory tree.
        """
        project_dir = project_dir if project_dir else work_project_dir if work_project_dir else os.getcwd()
        self.tree_structure = "root: " + project_dir + "\n"

        base_level = project_dir.count(os.sep)
        for root, dirs, files in os.walk(project_dir, topdown=True):
            level = root.count(os.sep) - base_level
            subdir = os.path.basename(root)
            indent_level = self.indent * level

            # Directly append result from handle_ignoreds to the self.tree_structure
            self.tree_structure += self.handle_ignoreds(subdir, dirs, indent_level)
            if dirs == []:  # If ignored, stop processing
                continue
            if max_depth is not None and level >= max_depth:
                self.tree_structure += f"{indent_level}|-- {subdir}/\n{indent_level}{self.disc_sym}\n"
                dirs[:] = []  # Stop descending into deeper directories
                continue

            # Add directory to the tree
            self.tree_structure += f"{indent_level}|-- {subdir}/\n"
            self.get_files(files, root, indent_level, file_match_regex, work_file_name)
        else:
            self.tree_structure += f"{indent_level}|-- {subdir}/\n"
            self.get_files(files, root, indent_level, file_match_regex, work_file_name)
        self.workfile_to_front(work_file_name, *args, **kwargs)
        return self.tree_structure

    def get_files(self, files, root, indent_level, file_match_regex, work_file_name):
        for file in files:
            if work_file_name and file.split('.')[0] == work_file_name:
                self.tree_structure += ( 
                                    f"{indent_level}{self.indent}|-- "
                                    f"{Fore.BLUE}{file}{Fore.RESET}\n"
                                    )
                self.find_match(root, file, work_file_name, *args, **kwargs)
            else:
                self.tree_structure += f"{indent_level}{self.indent}|-- {file}\n"
            if file_match_regex:
                self.find_match(root, file, file_match_regex, *args, **kwargs)

    def workfile_to_front(self, work_file_name: str, *args, **kwargs) -> None:
        """
        If work_file_name matches any file in self.matched_files (without extension),
        move that file's full path to the front of the list.
        
        Args:
            work_file_name (str): File name without extension to search for
        """
        # Find the full path that matches work_file_name (if any)
        matching_path = next(
            (path for path in self.matched_files 
             if os.path.splitext(os.path.basename(path))[0] == work_file_name),
            None
        )
        
        if matching_path:
            # Remove the matching path and add it to the front
            self.matched_files = [matching_path] + list(self.matched_files - {matching_path})

    def __call__(self, *args, **kwargs):
        """
        Enable the class instance to be called directly.
        Returns a dictionary containing the tree structure and matched files.

        Args:
            project_dir (str): The path to the project directory.
            max_depth (int): The maximum depth for directory traversal.

        Returns:
            dict: A dictionary with 'tree' and 'file_matches' keys.
        """
        tree_output = self.mk_tree(*args, **kwargs)
        selected_files = self.load_matched_files(*args, **kwargs)
        return {
            'tree': tree_output,
            'file_matches': self.matched_files,
            'selected_files': selected_files,
        }

    def load_matched_files(self, *args, **kwargs):
        selected_files = []
        default_ignore_files = kwargs.pop('default_ignore_files', [])
        file_paths_in_defaults = [file_path for file_path in self.matched_files if file_path.startswith(tuple(default_ignore_files))]
        # Filter out files that are already marked as ignored
        remaining_file_paths = [file_path for file_path in self.matched_files if file_path not in file_paths_in_defaults]
        for file_path in remaining_file_paths:
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    file_content = file.read()
                except UnicodeDecodeError:
                    print(f"{Fore.RED}Error reading file: {file_path}{Fore.RESET}")
                    continue
                selected_files.append(
                        {
                            'file_path': file_path,
                            'file_type': self.file_types.get(os.path.splitext(file_path)[1]),
                            'file_content': file_content, 
                        }
                                    )
        return selected_files

    def parse_tree(self, tree: str, *args, **kwargs):
        """
        Parse the tree string into a list of directories and file paths.

        Args:
            tree (str): The tree string to parse.

        Returns:
            List[Tuple[str, bool]]: List of tuples containing the path and whether it's a 
            directory.
        """
        paths = []
        temps = []
        normalized = tree.strip().split('\n')

        for line in normalized:
            if not line.strip() or line.startswith('<'):
                continue

            level = line.count(self.indent)
            line = line.strip().replace("|--", "").strip()
            is_dir = line.endswith('/')
            line = line.rstrip('/')

            if len(temps) < level:
                temps.append(line)
            else:
                temps = temps[:level]
                temps.append(line)

            paths.append((os.path.join(*temps), is_dir))

        return paths


def main(*args, load=False, **kwargs):
    """
    Main function to create a directory tree and collect matched files.
    
    All arguments are passed as kwargs from argparse.
    """
    # Remove ignores from kwargs and handle it separately
    ignores = kwargs.pop('ignores', None)
    tree = Tree(ignores=ignores, **kwargs)  # Pass ignores explicitly, the rest as **kwargs
    result = tree(project_dir=os.getcwd(), **kwargs)  # Use __call__
    print(result['tree'])
    
    if result['selected_files']:
        print("\nMatched Files:")
        for file in result['selected_files']:
            if load:
                print(f"{Fore.YELLOW}\n\nContent of {file['file_path']}:{Fore.RESET}\n")
                print(file['file_content'])
            else:
                print(file['file_path'])


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("-i", "--ignores", nargs="+", default=None, 
                                        help="Directories to ignore")
    p.add_argument("-r", "--file_match_regex", type=str, default=None, 
                                        help="Regex to match files")
    p.add_argument("--max_depth", type=int, default=None, 
                                        help="Maximum depth for directory traversal")
    p.add_argument("-l", "--load", action='store_true', help="Load matched files")
    
    # Parse arguments
    args = p.parse_args()
    
    # Convert argparse Namespace to dictionary and pass it to the main function
    main(**vars(args))
