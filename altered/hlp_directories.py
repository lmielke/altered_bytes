import os
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