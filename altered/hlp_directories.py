import os

def cleanup_data_dir(data_dir:str, *args, max_entries: int = 10, exts:set=None, **kwargs) -> None:
    """
    Clean up old CSV files in the data directory, keeping only the most recent ones.

    Args:
        max_entries (int): Maximum number of files to keep.
    """
    all_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
    if exts is not None:
        all_paths = [p for p in all_paths if os.path.splitext(p)[1].strip('.') in exts]
    all_paths.sort(key=os.path.getctime, reverse=True)
    for old_file in all_paths[max_entries - 1:]:
        os.remove(old_file)