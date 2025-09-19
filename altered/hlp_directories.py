import os, time, yaml
import altered.settings as sts
from colorama import Fore, Style
from contextlib import contextmanager

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
    # we also derrive the project name (pr_name) and package_name (pg_name)
    pr_name = os.path.basename(project_dir) if is_package and project_dir else None
    pg_name = os.path.basename(package_dir) if is_package and package_dir else None
    return {
            'pr_name': pr_name,
            'pg_name': pg_name,
            'work_dir': work_dir, 
            'project_dir': project_dir, 
            'package_dir': package_dir, 
            'is_package': is_package,
            }

def manage_log_files(log_dir:str, age_days:int=15, log_max:int=20, *args, **kwargs) -> int:
    """
    Removes log files in the specified directory that are older than the specified age.
    """
    cutoff = time.time() - (age_days * 86400)  # 86400 seconds in a day
    if not os.path.isdir(log_dir):
        print(f"{Fore.RED}Log directory {log_dir} does not exist.{Style.RESET_ALL}")
        return 0
    log_files = os.listdir(log_dir)
    to_remove, removed_files = len(log_files) - log_max, 0
    for i, filename in enumerate(log_files):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < cutoff or i < to_remove:
                try:
                    os.remove(file_path)
                    removed_files += 1
                    print(f"{Fore.GREEN}Removed old log file: {file_path}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error removing file {file_path}: {e}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Total old log files removed: {removed_files}{Style.RESET_ALL}")
    return removed_files

@contextmanager
def temp_chdir(target_dir: str) -> None:
    """
    Context manager for temporarily changing the current working directory.

    Parameters:
    target_dir (str): The target directory to change to.

    Yields:
    None
    """
    original_dir = os.getcwd()
    try:
        os.chdir(target_dir)
        yield
    finally:
        os.chdir(original_dir)
