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

def normalize_path(path: str, *args, **kwargs) -> str:
    """
    WHY: Canonicalize user-supplied paths consistently across OS.
    """
    if not path:
        return path
    p = os.path.expanduser(path)
    if not os.path.isabs(p):
        p = os.path.abspath(os.path.join(os.getcwd(), p))
    return os.path.normpath(p)

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
