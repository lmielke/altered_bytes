import os
import re
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List, Tuple
from colorama import Fore
from datetime import datetime as dt
import altered.settings as sts
import altered.hlp_directories as hlp_dirs

class FileStorage:
    file_ext_csv = 'csv'
    file_ext_npy = 'npy'
    default_data_dir = os.path.join(sts.resources_dir, 'data')
    fields_path = os.path.join(default_data_dir, 'data_Data_load_fields_data.yml')
    default_fields_path = os.path.join(default_data_dir, 'data_Data_load_fields_default.yml')

    def __init__(self, *args, name: str, data_file_name: Optional[str] = None, **kwargs):
        self.name = name
        self.time_stamp = dt.now()
        self.data_file_name = data_file_name
        self.data_dir = self.mk_data_dir(*args, **kwargs)

    def mk_data_dir(self, *args, data_dir: Optional[str] = None, **kwargs) -> str:
        data_dir = os.path.join(data_dir if data_dir else self.default_data_dir, self.name)
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    def construct_file_path(self, *args, data_dir:str=None, **kwargs) -> str:
        """Constructs the file path based on the file name and extension."""
        file_name = self.construct_file_name(self.data_dir, *args, **kwargs)
        self.data_path = os.path.join(self.data_dir, file_name)
        return self.data_path

    def construct_file_name(self, data_dir:str, *args, 
                            file_ext:str, data_file_name: Optional[str]=None, **kwargs,
        ) -> str:
        data_file_name = data_file_name if data_file_name is not None else \
                            self.data_file_name if self.data_file_name is not None else None
        if data_file_name is None:
            return f"{self.name}_{self.time_stamp.strftime(sts.time_strf)[:-7]}.{file_ext}"
        if '.' in data_file_name:
            data_file_name, file_ext = os.path.splitext(data_file_name)
        if file_ext.startswith('.'):
            file_ext = file_ext[1:]
        return self.from_latest_file(data_dir, data_file_name, file_ext)

    def from_latest_file(self, data_dir:str, data_file_name:str, file_ext:str) -> str:
        # data_file_name can be like this: UT_Test_Data_2024-10-04_14-55-09 or
        # simply be the name: UT_Test_Data, in this case the latest file must be found
        # now we check if time_stamp is provided in the data_file_name
        data_file_split = re.split(rf'_({sts.time_stamp_regex})', data_file_name)
        if len(data_file_split) == 3:
            sorteds = sorted([f for f in os.listdir(data_dir) if data_file_name in f\
                                and f.endswith(f".{file_ext}")])
            if len(sorteds) == 0:
                return f"{data_file_name}.{file_ext}"
        else:
            sorteds = sorted([f for f in os.listdir(data_dir) if f.endswith(f".{file_ext}")])
            if len(sorteds) == 0:
                time_stamp = self.time_stamp.strftime(sts.time_strf)[:-7]
                return f"{data_file_name}_{time_stamp}.{file_ext}"
        return sorteds[-1]

    def save_to_disk(self, *args, data:object, verbose:int=0, **kwargs) -> str:
        """
        Saves data to disk, supports both CSV (pandas.DataFrame) and NPY (NumPy array).
        """
        data_path = self.construct_file_path(*args,
                                file_ext = 'csv' if isinstance(data, pd.DataFrame) else 'npy',
                                            **kwargs)
        data_path = data_path if data_path else self.data_path
        if verbose >= 1:
            print(f"{Fore.MAGENTA}FileStorage.save_to_disk: Saving {self.name} "
                  f"to:{Fore.RESET} {data_path}")
        # Corrected file extension check
        if isinstance(data, pd.DataFrame):
            if isinstance(data, pd.DataFrame):
                data.to_csv(f"{data_path}", index=False)
            else:
                raise ValueError(f"Expected data to be a pandas DataFrame for .csv, "
                                 f"but got {type(data)}.")
        elif isinstance(data, np.ndarray):
            if isinstance(data, np.ndarray):
                np.save(f"{data_path}", data)
            else:
                raise ValueError(f"Expected data to be a NumPy array for .npy, "
                                 f"but got {type(data)}.")

        self.cleanup_data_dir(*args, verbose=verbose, **kwargs)
        return data_path

    def load_from_disk(self, *args, verbose:int=0, **kwargs) -> Optional[object]:
        """
        Loads data from disk, returns a DataFrame for CSV and a NumPy array for NPY formats.
        """
        data_path = self.construct_file_path(*args, **kwargs)
        if not os.path.isfile(data_path):
            return None
        if verbose >= 1:
            print(f"{Fore.MAGENTA}FileStorage.load_from_disk:{Fore.RESET} "
                  f"{self.data_file_name = } -> {data_path = }")
        # Corrected file extension check
        if data_path.endswith('.csv'):
            return pd.read_csv(f"{data_path}")
        elif data_path.endswith('.npy'):
            return np.load(f"{data_path}", allow_pickle=True)

    def cleanup_data_dir(
        self, *args, max_files: int = sts.max_files, exts: set = sts.data_file_exts, **kwargs,
    ) -> None:
        hlp_dirs.cleanup_data_dir(self.data_dir, max_files, exts, *args, **kwargs)
