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

def set_workdir(*args, work_dir: str = None, **kwargs):
    """
    Sets work_package_dir and work_project_dir based on provided or current work_dir.
    Detects both independently. They may be identical or different.
    """
    work_dir = os.path.abspath(work_dir or os.getcwd())
    parent_dir = os.path.dirname(work_dir)
    project_key_files = {'Pipfile', 'pyproject.toml', 'requirements.txt'}
    # --- Detect package dir
    work_package_dir = None
    if '__init__.py' in os.listdir(work_dir):
        work_package_dir = work_dir
    elif '__init__.py' in os.listdir(parent_dir):
        work_package_dir = parent_dir
    # --- Detect project dir
    work_project_dir = None
    if any(f in os.listdir(work_dir) for f in project_key_files):
        work_project_dir = work_dir
        is_package = True
    elif any(f in os.listdir(parent_dir) for f in project_key_files):
        work_project_dir = parent_dir
        is_package = True
    else:
        is_package = False
        work_project_dir = work_dir
    # os.environ['work_package_dir'] = work_package_dir if work_package_dir is not None else ''
    # os.environ['work_project_dir'] = work_project_dir if work_project_dir is not None else ''
    return {
            'work_package_dir': work_package_dir, 
            'work_project_dir': work_project_dir, 
            'is_package': is_package,
            }