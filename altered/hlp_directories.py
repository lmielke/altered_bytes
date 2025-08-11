import os, yaml
import altered.settings as sts
from colorama import Fore, Style

def cleanup_data_dir(data_dir:str, max_files:int=sts.max_files, exts:set=None, *args, 
    verbose:int=0, **kwargs, ) -> None:
    """
    Clean up old CSV files in the data directory, keeping only the most recent ones.

    Args:
        max_files (int): Maximum number of files to keep.
    """
    if verbose:
        print(  f"\n{Fore.MAGENTA}Cleaning up{Fore.RESET} {data_dir} directory. "
                f"Keeping only the most recent {Fore.MAGENTA}{max_files}{Fore.RESET} files "
                f"removing files with {Fore.MAGENTA}{exts}{Fore.RESET} extension."
        )
    all_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
    if exts is not None:
        all_paths = [p for p in all_paths if os.path.splitext(p)[1].strip('.') in exts]
    # we use FIFO (First In First Out) for removing the files 
    all_paths.sort(key=os.path.getctime, reverse=True)
    to_remove = all_paths[max_files - 1:]
    for old_file in to_remove:
        if verbose:
            print(f"{Fore.YELLOW}Removing: {Fore.RESET} {old_file}")
        os.remove(old_file)

def normalize_path(path:str, *args, **kwargs) -> str:
    """
    Normalize the given path to ensure it is absolute and uses the correct separators.
    """
    n_path = ""
    if not path:
        return path
    if path.startswith('~'):
        n_path = os.path.expanduser(path)
    elif path.startswith('/'):
        n_path = os.path.join(os.sep, path[1:])
    elif path.startswith('.'):
        n_path = os.path.join(os.getcwd(), path[2:])
    if os.path.exists(n_path):
        return os.path.normpath(n_path)
    return path

def write_tempfile(*args, api: str, content: str, up_file: str = None, **kwargs):
    """
    Writes the generated content JSON back to the original up_file, if provided.
    """
    if not up_file:
        return  # Skip if no output path is specified
    up_file = normalize_path(up_file, *args, **kwargs)
    out_str = f"\n{api}_response:\n{content.strip()}\n"
    try:
        with open(up_file, 'a', encoding='utf-8') as f:
            f.write(out_str)
    except Exception as e:
        print(f"{Fore.RED}Failed to write content to file {up_file}: {e}{Fore.RESET}")

def set_workdir(*args, work_dir:str=None, **kwargs):
    """
    Sets work_dir and project_dir based on provided or current work_dir.
    Detects both independently. They may be identical or different.
    """
    work_dir = os.path.abspath(work_dir if work_dir is not None else os.getcwd())
    parent_dir = os.path.dirname(work_dir)
    project_key_file, package_key_file = 'setup.py', '__main__.py'
    # based on the key files we want to populate package information
    project_dir, package_dir, is_package = None, None, False
    # --- Detect package dir
    if project_key_file in os.listdir(work_dir):
        project_dir = work_dir
    elif package_key_file in os.listdir(work_dir):
        package_dir = work_dir
        is_package = True
        if project_key_file in os.listdir(os.path.dirname(work_dir)):
            project_dir = os.path.dirname(work_dir)
    if project_dir == work_dir:
        for d in os.listdir(project_dir):
            candidate = os.path.join(project_dir, d)
            if os.path.isdir(candidate) and package_key_file in os.listdir(candidate):
                package_dir = candidate
                is_package = True

    return {
            'work_dir': work_dir, 
            'project_dir': project_dir, 
            'package_dir': package_dir, 
            'is_package': is_package,
            }