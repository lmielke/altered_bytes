import os
import re
from typing import Set

import altered.settings as sts


class Tree:
    default_ignores = {'.git', 'altered.egg-info', 'build', '__pycache__', 'logs'}
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

    def mk_tree(self, *args, project_dir:str=sts.project_dir, max_depth:int=2, file_match_regex:str=None, **kwargs) -> str:
        """
        Generate an uncolorized string representation of the directory tree and collect
        matched files.

        Args:
            project_dir (str): The path to the project directory.
            max_depth (int): The maximum depth for directory traversal (None for unlimited).

        Returns:
            str: A string representing the uncolorized directory tree.
        """
        tree_structure = ""
        base_level = project_dir.count(os.sep)

        for root, dirs, files in os.walk(project_dir, topdown=True):
            level = root.count(os.sep) - base_level
            subdir = os.path.basename(root)
            indent_level = self.indent * level

            # Directly append result from handle_ignoreds to the tree_structure
            tree_structure += self.handle_ignoreds(subdir, dirs, indent_level)
            if dirs == []:  # If ignored, stop processing
                continue

            if max_depth is not None and level >= max_depth:
                tree_structure += f"{indent_level}|-- {subdir}/\n{indent_level}{self.disc_sym}\n"
                dirs[:] = []  # Stop descending into deeper directories
                continue

            # Add directory to the tree
            tree_structure += f"{indent_level}|-- {subdir}/\n"
            for file in files:
                tree_structure += f"{indent_level}{self.indent}|-- {file}\n"
                if file_match_regex:
                    self.find_match(root, file, file_match_regex, *args, **kwargs)
        return tree_structure

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
        for file_path in self.matched_files:
            with open(file_path, 'r') as file:
                selected_files.append(
                        {
                            'file_path': file_path,
                            'file_type': self.file_types.get(os.path.splitext(file_path)[1]),
                            'file_content': file.read(), 
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


def main(**kwargs):
    """
    Main function to create a directory tree and collect matched files.
    
    All arguments are passed as kwargs from argparse.
    """
    # Remove ignores from kwargs and handle it separately
    ignores = kwargs.pop('ignores', None)
    tree = Tree(ignores=ignores, **kwargs)  # Pass ignores explicitly, the rest as **kwargs
    result = tree(project_dir=os.getcwd(), **kwargs)  # Use __call__
    print(result['tree'])
    
    if result['file_matches']:
        print("\nMatched Files:")
        for file in result['file_matches']:
            print(file)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("-i", "--ignores", nargs="+", default=None, 
                                        help="Directories to ignore")
    p.add_argument("-r", "--file_match_regex", type=str, default=None, 
                                        help="Regex to match files")
    p.add_argument("--max_depth", type=int, default=None, 
                                        help="Maximum depth for directory traversal")
    
    # Parse arguments
    args = p.parse_args()
    
    # Convert argparse Namespace to dictionary and pass it to the main function
    main(**vars(args))
