
"""
This module defines the Data class, which facilitates the management of structured
data in a tabular format. The Data class is designed to handle various data-related
tasks, such as loading and saving data from/to disk, managing fields defined in a
YAML file, and adding new records to the data table.

The class leverages the pandas library for efficient data manipulation and provides
methods for working with data in a CSV format. It also includes utilities for 
displaying the data in a readable table format using the tabulate library.

Key Objects:
- Fields and Field properties using a props dictionary.
- Data Location handling
- Recent Record added to Data
- Data as pd.DataFrame

Modules and Libraries Used:
- pandas: For DataFrame management and data manipulation.
- yaml: For parsing field definitions from YAML files.
- tabulate: For pretty-printing tabular data.
- colorama: For adding color to the terminal output.
- datetime: For timestamp management.
- os, re, json, shutil: Various standard libraries for file and string operations.

Related Documents:
- python -m unittest altered.test.test_ut.test_data
- test data: sts.project_dir/altered/resources/data/data_name/*_fields.yml
"""

import base64, csv, hashlib, json, os, re, shutil, yaml
import pandas as pd
from tabulate import tabulate as tb
from datetime import datetime as dt
from typing import List, Dict, Any, Optional
from colorama import Fore, Style
import altered.settings as sts
import altered.hlp_directories as hlp_dirs
import altered.hlp_printing as hlp_print

default_fields = 'default_fields.yml'
props_ident = r'(?:#\s*meta:\s+)(.*)\n'


class Data:
    """
    The Data class is used for managing structured data interactions in a tabular format.
    It handles tasks like loading/saving data, managing fields defined in a YAML file,
    and adding new records to the table.
    """

    def __init__(self, name: str, *args, **kwargs):
        """
        Initialize the Data object with a name and optional fields.

        Args:
            name (str): The name of the dataset.
            fields (Optional[Dict[str, str]]): Optional dictionary to specify fields.
        """
        self.name:str = name
        self.time_stamp:dt = dt.now()
        self.data_dir:Optional[str] = None
        self.fields:Dict[str, Any] = {}
        self.record:Dict[str, Any] = {}
        self.dtypes:Dict[str, Any] = {}

        # getattr(self, self.name):pd.DataFrame = pd.DataFrame(columns=[])
        # the main data object is named after self.name so we can call it like self.[self.name]
        setattr(self, self.name, pd.DataFrame(columns=[]))
        self.mk_data_dir(*args, **kwargs)
        self.load_from_disk(*args, **kwargs)
        self.load_fields(*args, **kwargs)
        self.create_table(*args, **kwargs)
        self.add_init_record(*args, **kwargs)

    def mk_data_dir(self, *args, data_dir:Optional[str]=None, **kwargs) -> str:
        """
        Create the data directory if it does not exist.

        Args:
            data_dir (Optional[str]): Directory to store data files.

        Returns:
            str: Path to the data directory.
        """
        self.data_dir = data_dir if data_dir else os.path.join(sts.data_dir, self.name)
        os.makedirs(self.data_dir, exist_ok=True)
        return self.data_dir

    def load_fields(self, *args, fields_path:Optional[str]=default_fields, **kwargs,
        ) -> Dict[str, Any]:
        """
        Load field definitions from a YAML file.

        Args:
            fields_path (Optional[str]): Path to the fields_path YAML file.

        Returns:
            Dict[str, Any]: Loaded field definitions.
        """
        file_path = os.path.join(sts.data_dir, fields_path)
        with open(file_path, 'r') as fields_file:
            fields_content = fields_file.read()
            for prop in re.findall(props_ident, fields_content):
                _props = json.loads(prop.strip())
                self.fields[_props['name']] = _props
            fields_file.seek(0)
            self.record = yaml.safe_load(fields_file)
        return self.record

    def create_table(self, *args, **kwargs) -> None:
        """
        Create an initial DataFrame with the correct column types based on the 'type'
        field in the loaded YAML file.
        """
        if not getattr(self, self.name).empty:
            return
        self.dtypes = {field: properties['type'] for field, properties in self.fields.items()}
        columns = {field: pd.Series(dtype=dtype) for field, dtype in self.dtypes.items()}
        setattr(self, self.name, pd.DataFrame(columns).astype(self.dtypes))

    def add_init_record(self, *args, **kwargs) -> None:
        """
        Appends the initial record to the DataFrame. This is a meta record that is designed
        to contain information about the DataFrame and its content.
        """
        
        init_record = {k: self.record[vs['name']] for k, vs in self.fields.items()}
        init_record['timestamp'] = self.time_stamp
        # we dont use append here for future extentiabilty
        setattr(self, self.name, pd.DataFrame([init_record], 
                        columns=getattr(self, self.name).columns).astype(self.dtypes))

    def save_to_disk(self, *args, **kwargs) -> None:
        """
        Save the current DataFrame to disk as a CSV file.

        The filename is based on the current timestamp.
        """
        file_name = f"{self.time_stamp.strftime(sts.time_strf)[:-7]}.csv"
        file_path = os.path.join(self.data_dir, file_name)
        getattr(self, self.name).to_csv(file_path, index=False)

    def load_from_disk(self, *args, file_name:Optional[str]=None, **kwargs) -> None:
        """
        Load a DataFrame from a CSV file.

        Args:
            file_name (Optional[str]): Name of the file to load.
                If 'latest', the most recent file is loaded.
        """
        if file_name is None:
            return
        elif file_name == 'latest':
            file_names = [f for f in os.listdir(self.data_dir) if re.match(sts.data_regex, f)]
            if not file_names:
                raise FileNotFoundError(f"No files matching regex found in {self.data_dir}")
            file_path = os.path.join(self.data_dir, file_names[0])
        else:
            file_path = os.path.join(self.data_dir, file_name)
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
        setattr(self, self.name, pd.read_csv(file_path).astype(self.dtypes))

    def cleanup_data_dir(self, *args, max_entries:int=10, **kwargs) -> None:
        """
        Clean up old CSV files in the data directory, keeping only the most recent ones.

        Args:
            max_entries (int): Maximum number of files to keep.
        """
        hlp_dirs.cleanup_data_dir(self.data_dir, *args, max_entries=max_entries, **kwargs)

    def append(self, record:Dict[str, Any], *args, **kwargs) -> None:
        """
        Append a new record to the DataFrame.

        Args:
            record (Dict[str, Any]): The record to append.
        """
        for field in record:
            if field not in self.record:
                raise ValueError(f"Unknown field: {field}")
        if set(self.record) - set(record.keys()):
            raise ValueError(f"Missing fields: {set(self.record) - set(record.keys())}")
        if 'timestamp' in self.record:
            record['timestamp'] = dt.now()
        # here we appending the new record to the DataFrame. Because the dtypes are lost
        # Concatenate only if the new record_series is not empty or all-NA
        setattr(self, self.name,    pd.concat(
                                    [
                                        getattr(self, self.name), 
                                        pd.Series(record).to_frame().T.astype(self.dtypes),
                                    ],
                                            ignore_index=True,
                                    )
        )

    def show(self, *args, color:object=Fore.YELLOW, verbose:int=0, **kwargs) -> None:
        """
        Display the current DataFrame in a tabular format.
        """
        if getattr(self, self.name).empty:
            print("No data available.")
            return
        # prep texts for better readabiltiy
        df = getattr(self, self.name)
        df['content'] = df['content'].apply(lambda x: hlp_print.wrap_text(x))
        df['prompt'] = df['prompt'].apply(lambda x: hlp_print.wrap_text(x))
        # this only shows the columns of the df that have at least one value in it
        if verbose:
            df = getattr(self, self.name).to_dict(orient='records')
        else:
            df = getattr(self, self.name).dropna(axis=1, how='all').to_dict(orient='records')
        tbl = tb(df, headers="keys", tablefmt="grid")
        tbl = '\n'.join([f"{color}{l}{Fore.RESET}"if i == 2 else l 
                                                    for i, l in enumerate(tbl.split("\n"))])
        print(tbl)
