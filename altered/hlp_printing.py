"""
hlp_printing.py
"""
import re
from colorama import Fore, Style
import altered.settings as sts
from textwrap import wrap as tw
from tabulate import tabulate as tb

def wrap_text(text:str, *args, max_chars:int=sts.table_max_chars, **kwargs):
    if type(text) == str and len(text) > max_chars:
        wrapped = ''
        for line in text.split('\n'):
            if len(line) > max_chars:
                line = '\n'.join(tw(line, max_chars))
            wrapped += f"\n{line}"
        return wrapped
    return text


def pretty_prompt(prompt:str, *args, verbose:int=0, **kwargs) -> str:
    prompt = re.sub(r'<user_prompt>\s*</user_prompt>', '', prompt, flags=re.MULTILINE)
    if verbose >= 2:
        # we replace the <tags> in prompt with colorized tags
        p = prompt.replace('context>', f"{Fore.BLUE}context>{Fore.RESET}")
        p = p.replace('rag_db_matches>', f"{Fore.GREEN}rag_db_matches>{Fore.RESET}")
        p = p.replace('user_prompt>', f"{Fore.YELLOW}user_prompt>{Fore.RESET}")
        p = p.replace('previous_responses>', f"{Fore.CYAN}previous_responses>{Fore.RESET}")
        p = p.replace('INST>', f"{Fore.CYAN}INST>{Fore.RESET}")
        print(f"\n\n{Fore.CYAN}# pretty_prompt:{Fore.RESET} \n{p}")


def pretty_dict(name:str, d:dict, *args, **kwargs):
    print(f"\n{Fore.CYAN}#{name}.keys(): {Fore.RESET}{d.keys()}")
    for k, v in d.items():
        print(f"{Fore.CYAN}{k}: {Fore.RESET}{v}")

def dict_to_table(name:str, d:dict, *args, **kwargs):
    tbl_dict = dict(**d)
    tbl_dict[name] = tbl_dict.keys()
    for kk, vs in d.items():
        if type(vs) == str:
            tbl_dict[kk] = wrap_text(vs, *args, **kwargs)
        elif type(vs) == dict:
            tbl_dict[kk] = wrap_text('\n'.join([f"{Fore.CYAN}{k}{Fore.RESET}: {str(v)}" for k, v in vs.items()]))
        elif type(vs) == list:
            tbl_dict[kk] = wrap_text('\n'.join([str(v) for v in vs]))
    tbl = tb(tbl_dict.items(), headers=[f'name: {name}', 'value'], tablefmt='simple')
    colored_table_underline(tbl, *args, **kwargs)

def colored_table_underline(tbl, *args, up_to:int=0, color=Fore.CYAN, **kwargs):
    print('\n')
    for i, line in enumerate(tbl.split('\n')):
        if i <= up_to:
            print(f"{color}{line}{Fore.RESET}")
        else:
            print(line)