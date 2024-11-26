from typing import Any, Dict
from colorama import Fore, Style, Back
from tabulate import tabulate as tb
import numpy as np
import re, time

class PromptStats:

    # Token length divisor describes the ratio tokens to characters (default is 3)
    tkd = 3
    sub_total_prefix = "Sub-Total: "
    sample_len = 100

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the class and variables for length tracking.

        Args:
            *args, **kwargs: Accepts and ignores additional arguments.
        """
        self.lc = [Fore.BLUE, Fore.CYAN, Fore.MAGENTA]
        self.backs = [Back.BLUE, Back.CYAN, Back.MAGENTA]
        self.total_color, self.llc = Fore.YELLOW, Fore.WHITE

    def __call__(self, up_to: int, *args, **kwargs) -> str:
        """
        Processes the dictionary and calculates both character and token lengths.
        Constructs the table and returns the colored table string.

        Args:
            up_to: The maximum level to construct the table.
            data_dict: The dictionary to process.
            *args, **kwargs: Accepts and ignores additional arguments.

        Returns:
            The colored table as a string.
        """
        self.results = {}
        self.total = np.array([0, 0], dtype=int)
        self.tbl_data = []
        self._process_level(*args, **kwargs)
        self.construct_table(up_to, *args, **kwargs)
        return self.color_table(up_to, *args, **kwargs)

    def _process_level(self, level: int=0, *args, data_dict: Dict[Any, Any], 
                                                pk: str = 'root', **kwargs) -> int:
        """
        Recursively processes the dictionary and calculates both token and character lengths.
        
        Args:
            level: Current recursion level (0 for top-level).
            data_dict: The dictionary to process.
            *args, **kwargs: Accepts and ignores additional arguments.

        Returns:
            The total length of the dictionary at this level.
        """
        # Initialize counters for each level
        l_len = 0
        for k, vs in data_dict.items():
            k_len = len(str(k))  # Length of the k (in characters)
            if isinstance(vs, dict):
                # Recursively process nested dictionaries
                vs_len = self._process_level(level+1, *args, data_dict=vs, pk=k, **kwargs)
            else:
                # Handle non-dictionary values (including None)
                vs_len = len(str(vs)) if vs else 0
            kv_len = k_len + vs_len
            l_len += kv_len
            vs_str = (f"{str(vs)[:self.sample_len]}..."if vs and 
                            len(str(vs)) > self.sample_len else str(vs) if vs else 'None')
            if self.results.get(level):
                self.results[level][f"{pk}.{k}"] = (kv_len, kv_len // self.tkd, vs_str, pk)
            else:
                self.results[level] = {f"{pk}.{k}": (kv_len, kv_len // self.tkd, vs_str, pk)}
        if self.results.get(level):
            self.results[level][f"{pk}.len(key)"] = (len(pk), len(pk) // self.tkd, pk, pk)
        return l_len

    def construct_table(self, up_to:int, level:int=0, pk:str='root.root', *args, **kwargs
        ) -> None:
        """
        Constructs the table up to the specified level, recursively including nested keys 
        and sub-totals.

        Args:
            up_to: The maximum level to construct.
            level: Current recursion level (default is 0).
            pk: Parent key for filtering (default is 'root').
            *args, **kwargs: Accepts and ignores additional arguments.
        """
        found, indent = False, '    ' * level
        for key, (num_char, num_tk, text, ll_p_key) in self.results[level].items():
            if not ll_p_key == pk.split('.')[1]:
                continue
            found = True
            if level >= up_to:
                self.total += np.array([num_char, num_tk], dtype=int)
                self.tbl_data.append([f"{indent}{key}", num_char, num_tk, text, level])
            else:
                tbl_ix = len(self.tbl_data)
                r_found = self.construct_table(up_to, level + 1, key, *args, **kwargs)
                if r_found:
                    prefix = self.sub_total_prefix
                else:
                    prefix = ''
                    self.total += np.array([num_char, num_tk], dtype=int)
                self.tbl_data.insert(tbl_ix, [f"{indent}{key} {prefix}", num_char, 
                                                                    num_tk, text, level])
        if level == 0:
            self.tbl_data.append(['Total', self.total[0], self.total[1], '', 0])
        return found

    def color_table(self, up_to:int, *args, **kwargs) -> str:
        """
        Applies color to the table rows based on the row type:
        - Subtotal rows: Cyan
        - Total row: Yellow
        - Regular rows: White
        *args, **kwargs: Accepts and ignores additional arguments.

        Returns:
            The colored table as a string.
        """
        colcheck = lambda item: f"{Fore.RED}{item}{Fore.RESET}" if item >= 1000 else f"{item}"
        colored_table = []
        
        for row in self.tbl_data:
            if "Total" in row[0] and not self.sub_total_prefix in row[0]:
                # Apply blue color to the final total row
                colored_row = [f"{Back.MAGENTA}{item}{Style.RESET_ALL}" for item in row]
            elif self.sub_total_prefix in row[0]:
                colored_row = [
                        f"{self.backs[row[-1]]}{self.llc}{item}{Style.RESET_ALL}" 
                            if i == 1 or i == 2 
                            else f"{self.lc[row[-1]]}{item}{Style.RESET_ALL}" 
                                for i, item in enumerate(row)
                    ]
            elif 'len(key)' in row[0]:
                # we color every element in gray
                colored_row = [f"{Style.DIM}{item}{Fore.RESET}" for item in row]
            elif up_to == row[-1]:
                # Apply cyan color to subtotal rows
                colored_row = [f"{self.llc}{item}{Fore.RESET}" if type(item) != int 
                                                    else colcheck(item) for item in row]
            else:
                # Apply cyan color to subtotal rows
                colored_row = [f"{self.lc[row[-1]]}{item}{Style.RESET_ALL}" 
                                if type(item) != int else colcheck(item)  for item in row]
            colored_table.append(colored_row)
        # Create and return the colored table as a string
        return tb(colored_table,headers=['Key', 'Char Len', 'Token Len', 'Value', 'Level'], 
                                tablefmt='pretty',
                                showindex=False, 
                                stralign="left",
                                )
