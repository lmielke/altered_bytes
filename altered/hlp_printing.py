"""
hlp_printing.py
"""
import re
from colorama import Fore, Style
import altered.settings as sts
from textwrap import wrap as tw
from tabulate import tabulate as tb

def wrap_text(text:str, *args, max_chars:int=sts.table_max_chars, **kwargs):
    max_chars = normalize_max_chars(max_chars, text, *args, **kwargs)
    if type(text) == str and len(text) > max_chars:
        wrapped = ''
        for line in text.split('\n'):
            if len(line) > max_chars:
                line = '\n'.join(tw(line, max_chars))
            wrapped += f"\n{line}"
        return wrapped.strip()
    return text


def pretty_prompt(prompt:str, *args, verbose:int=0, **kwargs) -> str:
    prompt = re.sub(r'<user_prompt>\s*</user_prompt>', '', prompt, flags=re.MULTILINE)
        # we replace the <tags> in prompt with colorized tags
    p = (
            prompt.replace('context>', f"{Fore.BLUE}context{Fore.RESET}>")
                .replace('rag_db_matches>', f"{Fore.GREEN}rag_db_matches{Fore.RESET}>")
                .replace('user_prompt>', f"{Fore.YELLOW}user_prompt{Fore.RESET}>")
                .replace('previous_responses>', f"{Fore.CYAN}previous_responses{Fore.RESET}>")
                .replace('INST>', f"{Fore.CYAN}INST{Fore.RESET}>")
        )
    if verbose >= 2:
        print(f"\n\n{Fore.CYAN}# pretty_prompt:{Fore.RESET} \n{p}")
    return p


def pretty_dict(name:str, d:dict, *args, **kwargs):
    print(f"\n{Fore.CYAN}#{name}.keys(): {Fore.RESET}{d.keys()}")
    for k, v in d.items():
        print(f"{Fore.CYAN}{k}: {Fore.RESET}{v}")

def dict_to_table(name:str, d:dict, *args, **kwargs):
    tbl_dict = wrap_table(d, *args, **kwargs)
    tbl_dict[name] = tbl_dict.keys()
    tbl = tb(tbl_dict.items(), headers=[f'name: {name}', 'value'], tablefmt='simple')
    colored_table_underline(tbl, *args, **kwargs)

def colored_table_underline(tbl, *args, up_to:int=0, color=Fore.CYAN, **kwargs):
    print('\n')
    for i, line in enumerate(tbl.split('\n')):
        if i <= up_to:
            print(f"{color}{line}{Fore.RESET}")
        else:
            print(line)

def records_to_table(name:str, records:list, *args, **kwargs):
    # Extract headers from the keys of the first result
    wrapped_records = []
    for record in records:
        wrapped_records.append(wrap_table(record, *args, **kwargs))
    headers = records[0].keys()
    # Convert d to a list of values for tabulation
    table = [key.values() for key in wrapped_records]

    # Print the table using tabulate
    colored_table_underline(tb(table, headers=headers), *args, **kwargs)


def dict_to_table_v(name:str, d: dict, *args, **kwargs):
    """
    Prints the dictionary with keys as column headers and values as rows.
    Wraps long text using wrap_text function.
    """
    headers = list(d.keys())  # Extract keys for column headers
    row = []  # The row of values
    for key, value in d.items():
        if isinstance(value, str):
            row.append(wrap_text(value, *args, **kwargs))
        elif isinstance(value, dict):
            # If the value is another dictionary, format it for display
            row.append(
                wrap_text(
                    '\n'.join([f"{Fore.CYAN}{k}{Fore.RESET}: {str(v)}" for k, v in value.items()]),
                    **kwargs,
                )
            )
        elif isinstance(value, list):
            # If the value is a list, join the list into a string
            row.append(
                wrap_text(
                    '\n'.join([str(v) for v in value]),
                    **kwargs,
                )
            )
        else:
            # Handle any other data types (e.g., numbers, bools)
            row.append(str(value))
    # Use tabulate to create the table
    tbl = tb([row], headers=headers, tablefmt='simple')
    colored_table_underline(tbl, *args, **kwargs)

def wrap_table(d:dict, *args, **kwargs):
    tbl_dict = dict(**d)
    for kk, vs in d.items():
        if type(vs) == str:
            tbl_dict[kk] = wrap_text(vs, *args, **kwargs)
        elif type(vs) == dict:
            tbl_dict[kk] = wrap_text('\n'.join([f"{Fore.CYAN}{k}{Fore.RESET}: {str(v)}" for k, v in vs.items()]))
        elif type(vs) == list:
            tbl_dict[kk] = wrap_text('\n'.join([str(v) for v in vs]))
    return tbl_dict

def normalize_max_chars(max_chars:int, text, *args, **kwargs):
    """
    some strings contain very short texts
    those texts can use a shorter max_chars than longer texts
    so we re-compute max_chars to result in a minimum of 3 lines
    """
    if len(text) <= 50:
        return max_chars // 4
    elif len(text) <= 128:
        return max_chars // 3
    elif len(text) <= 400:
        return max_chars // 2
    else:
        return int(max_chars * 1.3)
