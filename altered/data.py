import csv, json, os, re, shutil, yaml
import warnings
import pandas as pd
pd.options.display.max_colwidth = 120
from tabulate import tabulate as tb
from datetime import datetime as dt
from typing import List, Dict, Any, Optional
from colorama import Fore, Style

from altered.yml_parser import YmlParser
import altered.settings as sts
import altered.hlp_directories as hlp_dirs
import altered.hlp_printing as hlpp

from altered.data_file_storage import FileStorage


class Data:
    def __init__(self, *args, name: str, **kwargs):
        self.name = name
        self.time_stamp = dt.now()
        self.fs = FileStorage(*args, name=name, **kwargs)
        self.dtypes = {}
        self.load_fields(*args, **kwargs)
        self.ldf = pd.DataFrame(columns=[])
        self.load_from_disk(*args, **kwargs)
        self.create_table(*args, **kwargs)
        self.add_init_record(*args, **kwargs)

    def load_fields(self, *args, fields_paths: list = None, 
                    u_fields_paths: list = None, **kwargs):
        if u_fields_paths:
            fields_paths = u_fields_paths + [self.fs.fields_path]
        else:
            fields_paths = (fields_paths if fields_paths 
                            else [self.fs.default_fields_path])
            fields_paths += [self.fs.fields_path]
        self.fields = YmlParser(*args, fields_paths=fields_paths, **kwargs)
        self.columns = self.fields.fields['meta']
        return self.columns

    @property
    def mfields(self, *args, **kwargs):
        _mfields = {}
        for k, vs in self.columns.items():
            _mfields[vs.get('mapping_source', k)] = vs
        return _mfields

    def map_fields(self, record: dict, *args, **kwargs):
        _record = {}
        for k, vs in self.columns.items():
            _record[k] = record.get(vs.get('mapping_source', k))
        _record['timestamp'] = dt.now()
        return _record

    def create_table(self, *args, **kwargs) -> None:
        self.dtypes = {field: properties['type'] 
                       for field, properties in self.columns.items()}
        if not self.ldf.empty:
            return
        columns = {field: pd.Series(dtype=dtype) for field, dtype in self.dtypes.items()}
        self.ldf = pd.DataFrame(columns).astype(self.dtypes)

    def add_init_record(self, *args, **kwargs) -> None:
        if not self.ldf.empty:
            return
        init_record = {k: self.fields.data[vs['name']] for k, vs in self.columns.items()}
        init_record['name'] = self.name
        if init_record.get('timestamp') is None and 'timestamp' in init_record.keys():
            init_record['timestamp'] = self.time_stamp
        self.ldf = pd.DataFrame([init_record], columns=self.ldf.columns).astype(self.dtypes)

    def load_from_disk(self, *args, **kwargs) -> None:
        loaded_df = self.fs.load_from_disk(*args, file_ext='csv', **kwargs)
        if loaded_df is not None:
            self.ldf = loaded_df.astype(self.dtypes)

    def validate_record(self, record: Dict[str, Any], *args, **kwargs) -> bool:
        required_keys, columns = set(record), set(self.columns)
        if columns - required_keys:
            msg = f"{columns - required_keys}\n{columns = } - {required_keys = }"
            raise ValueError(f"{Fore.RED}Missing fields:{Fore.RESET} {msg}")
        if required_keys - columns:
            msg = f"{required_keys - columns}\n{columns = } - {required_keys = }"
            raise ValueError(f"{Fore.RED}Unknown fields:{Fore.RESET} {msg}")
        return True

    def append(self, record: Dict[str, Any], *args, **kwargs) -> None:
        record = self.map_fields(record, *args, **kwargs)
        self.validate_record(record, *args, **kwargs)
        # Use 'hash' as the index if it exists, otherwise, fallback to the length of the DataFrame
        record_idx = record.get('hash', len(self.ldf))
        self.add_new_categories(record)
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            self.ldf.loc[record_idx] = {k: v for k, v in record.items()}

    def add_new_categories(self, record: Dict[str, Any]) -> None:
        """
        Adds missing categories to categorical columns in bulk based on the record values.
        
        Args:
            record (Dict[str, Any]): The new record to be added, containing potential new 
            categories.
        """
        # Select only categorical columns
        for column in self.ldf.select_dtypes(include=['category']).columns:
            value = record.get(column)
            if value is not None and value not in self.ldf[column].cat.categories:
                self.ldf[column] = self.ldf[column].cat.add_categories([value])

    def show(self, *args, color: object = Fore.CYAN, verbose: int = 1, **kwargs) -> None:
        df = self.ldf.copy()
        for column in df.columns:
            if df[column].dtype in ['object', 'string']:
                df[column] = df[column].astype(str)
                max_len = df[column].str.len().max()
                if pd.notna(max_len) and max_len > sts.table_max_chars:
                    df[column] = df[column].apply(lambda x: hlpp.wrap_text(x) \
                                                                    if pd.notna(x) else x)
        if df.empty:
            print("No data available.")
            return
        if verbose >= 2:
            for col in df.select_dtypes(include='category').columns:
                df[col] = df[col].cat.add_categories([""]).fillna("")
            df = df.fillna(value="")
            df = df.to_dict(orient='records')
        elif verbose:
            df = df.dropna(axis=1, how='all').to_dict(orient='records')
        if verbose:
            tbl = tb(df, headers="keys", tablefmt="grid", showindex=True)
            tbl = '\n'.join([f"{color}{l}{Fore.RESET}" if i == 2 else l 
                             for i, l in enumerate(tbl.split("\n"))])
            print(f"\n{Fore.CYAN}Data.show(){Fore.RESET} with table "
                  f"{Fore.CYAN}name: {Fore.RESET}{self.name}, "
                  f"{Fore.CYAN}id: {Fore.RESET}{id(self.ldf)}, "
                  f"{Fore.CYAN}num_entries: {Fore.RESET}{len(self.ldf)}\n", tbl)

    def mk_history(self, *args, history: list = [], field: str = 'content', **kwargs,
        ) -> list[dict]:
        if not self.ldf[field].empty and (self.ldf[field].str.len() > 0).any():
            for i, row in self.ldf.iterrows():
                if isinstance(row[field], str):
                    history.append({'role': row['role'], field: row[field]})
                    # print(f"{Fore.GREEN}{i}: {Fore.RESET} {row[field]}"[:200].replace('\n', ' '))
        return history if history else None

    def save_to_disk(self, *args, **kwargs) -> str:
        return self.fs.save_to_disk(*args, data=self.ldf, **kwargs)