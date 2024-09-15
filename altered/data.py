
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

import csv, json, os, re, shutil, yaml
import pandas as pd
pd.options.display.max_colwidth = 120
from tabulate import tabulate as tb
from datetime import datetime as dt
from typing import List, Dict, Any, Optional
from colorama import Fore, Style

import altered.settings as sts
import altered.hlp_directories as hlp_dirs
import altered.hlp_printing as hlpp

default_fields = 'data__data_load_fields_default.yml'
meta_identifier = r'(?:#\s*meta:\s+)(.*)\n'


class Data:
    """
    The Data class is used for managing structured data interactions in a tabular format.
    It handles tasks like loading/saving data, managing fields defined in a YAML file,
    and adding new records to the table.
    """
    data_file_ext = 'csv'

    def __init__(self, *args, name:str, **kwargs):
        """
        Initialize the Data object with a name and optional fields.

        Args:
            name (str): The name of the dataset.
            fields (Optional[Dict[str, str]]): Optional dictionary to specify fields.
        """
        self.name:str = name
        self.time_stamp:dt = dt.now()
        self.data_dir:Optional[str] = self.mk_data_dir(*args, **kwargs)
        self.fields:Dict[str, Any] = {}
        self.record:Dict[str, Any] = {}
        self.dtypes:Dict[str, Any] = {}
        # the main data object is named like self.name so we can call it like self.[self.name]
        # NOTE: this is a DataFrame constructor inheriting from pd.DataFrame
        self.ldf = LabeledDataFrame(columns=[])
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
        data_dir = data_dir if data_dir else os.path.join(sts.data_dir, self.name)
        os.makedirs(data_dir, exist_ok=True)
        print(f"{Fore.CYAN}\nData {self.name = } directory:{Fore.RESET} {data_dir}")
        return data_dir

    def load_fields(self, *args, fields_path:Optional[str]=default_fields, **kwargs,
        ) -> Dict[str, Any]:
        """
        Load field definitions from a YAML file.

        Args:
            fields_path (Optional[str]): Path to the fields_path YAML file.

        Returns:
            Dict[str, Any]: Loaded field definitions.
        """
        self.fields_path = os.path.join(sts.data_dir, fields_path)
        with open(self.fields_path, 'r') as fields_file:
            fields_content = fields_file.read()
            for prop in re.findall(meta_identifier, fields_content):
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
        if not self.ldf.empty:
            return
        self.dtypes = {field: properties['type'] for field, properties in self.fields.items()}
        columns = {field: pd.Series(dtype=dtype) for field, dtype in self.dtypes.items()}
        self.ldf = LabeledDataFrame(columns).astype(self.dtypes)

    def add_init_record(self, *args, **kwargs) -> None:
        """
        Appends the initial record to the DataFrame. This is a meta record that is designed
        to contain information about the DataFrame and its content.
        """
        
        init_record = {k: self.record[vs['name']] for k, vs in self.fields.items()}
        init_record['timestamp'] = self.time_stamp
        init_record['name'] = self.name
        # we dont use append here for future extentiabilty
        self.ldf = LabeledDataFrame([init_record],
                        columns=self.ldf.columns).astype(self.dtypes)
        # we add labels and descriptions to the DataFrame. This can be used to send 
        # the DataFrame fields to a file or as Field Example to an LLM.
        self.ldf.fields.add_labels( name='Default Fields', 
                                                    labels=self.fields_path, 
                                                    description="Default Fields",
                                        )

    def save_to_disk(self, *args, verbose:int=0, **kwargs) -> None:

        """
        Save the current DataFrame to disk as a CSV file.

        The filename is based on the current timestamp.
        """
        data_file_name = f"{self.time_stamp.strftime(sts.time_strf)[:-7]}.{self.data_file_ext}"
        file_path = os.path.join(self.data_dir, data_file_name)
        if verbose >= 1: 
            print(  f"{Fore.MAGENTA}Data.save_to_disk: "
                            f"Saving {self.name} to:{Fore.RESET} {file_path}"
                            )
        self.ldf.to_csv(file_path, index=False)
        self.cleanup_data_dir(*args, verbose=verbose, **kwargs)
        return file_path

    def load_from_disk(self, *args, data_file_name:Optional[str]=None, verbose:int=0,
        **kwargs) -> None:
        """
        Load a DataFrame from a CSV file.

        Args:
            data_file_name (Optional[str]): Name of the file to load.
                If 'latest', the most recent file is loaded.
        """
        if data_file_name is None:
            return
        elif data_file_name == 'latest':
            file_names = [f for f in os.listdir(self.data_dir) 
                                                        if re.match(sts.data_regex, f)
                                                        and f.endswith(self.data_file_ext)]
            if not file_names:
                msg =   (
                            f"{Fore.RED}ERROR:{Fore.RESET}"
                            f" No files matching {sts.data_regex} found in {self.data_dir}"
                        )
                raise FileNotFoundError(msg)
            # we load the most recent file
            file_path = os.path.join(self.data_dir, file_names[-1])
        else:
            # we ensure that the file to be loaded has a valid file extension
            name, ext = os.path.splitext(data_file_name)[0], self.data_file_ext
            file_path = os.path.join(self.data_dir, f"{name}.{ext}")
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
        if verbose >= 2: 
            print(
                    f"{Fore.CYAN}Data.load_from_disk:{Fore.RESET}"
                    f" {data_file_name = } -> {file_path = }"
                    )
        self.ldf = pd.read_csv(file_path).astype(self.dtypes)
        return file_path

    def cleanup_data_dir(self, *args,   max_files:int=sts.max_files,
                                        exts:set=sts.data_file_exts,
        **kwargs) -> None:
        """
        Clean up old CSV files in the data directory, keeping only the most recent ones.

        Args:
            max_files (int): Maximum number of files to keep.
        """
        hlp_dirs.cleanup_data_dir(self.data_dir, max_files, exts, *args, **kwargs)

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
        self.ldf =    pd.concat(
                                    [
                                        self.ldf, 
                                        pd.Series(record).to_frame().T.astype(self.dtypes),
                                    ],
                                            ignore_index=True,
                                    )

    def show(self, *args, color:object=Fore.CYAN, verbose:int=0, **kwargs) -> None:
        """
        Display the current DataFrame in a tabular format.
        """
        if self.ldf.empty:
            print("No data available.")
            return
        # prep texts for better readabiltiy
        df = self.ldf
        df['content'] = df['content'].apply(lambda x: hlpp.wrap_text(x))
        df['prompt'] = df['prompt'].apply(lambda x: hlpp.wrap_text(x))
        # this only shows the columns of the df that have at least one value in it
        if verbose:
            df = self.ldf.to_dict(orient='records')
        else:
            df = self.ldf.dropna(axis=1, how='all').to_dict(orient='records')
        tbl = tb(df, headers="keys", tablefmt="grid")
        tbl = '\n'.join([f"{color}{l}{Fore.RESET}"if i == 2 else l 
                                                    for i, l in enumerate(tbl.split("\n"))])
        print(tbl)

    def mk_history(self, *args, history:list=[], **kwargs) -> list[dict]:
        if not self.ldf['content'].empty and (self.ldf['content'].str.len() > 0).any():
            # we add the chat history for context (check if needed)
            for i, row in self.ldf.iterrows():
                if isinstance(row['content'], str):
                    history.append({'role':row['role'], 'content': row['content']})
        return {'history': history if history else None}

from altered.yml_parser import YmlParser

class LabeledDataFrame(pd.DataFrame):
    """
    Allows to label the df columns with loaded labels from a YAML fields file.
    labels can be added like:
    df.fields.add_labels(name='Unittest', labels=fields_path.yml, description="Test DF")
    Then the labels can be accessed like:
    df.fields.describe() or simply df.fields()
    also the output format can be specified like:
    df.fields.describe(fmt='tbl/json/yml') 
    """
    
    @property
    def _constructor(self, *args, **kwargs):
        return LabeledDataFrame
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = YmlParser(*args, **kwargs)
        