"""
api_prompt.py
"""

from colorama import Fore, Style
from datetime import datetime as dt
import os, re, json, sys

# package imports
import altered.settings as sts
import altered.hlp_printing as hlpp
import altered.contracts as contracts
from altered.prompt import Prompt

required_args = {'user_prompt',}

def prompt(*args, api:str, **kwargs):
    """
    Display basic information about the system and configuration
    Returns a dictionary containing the information
    """
    kwargs.update(contracts.checks(*args, **kwargs))
    return Prompt(api, *args, **kwargs)(*args, **kwargs)
    # hlpp.pretty_prompt(prompt.data, *args, verbose=verbose, **kwargs)


def main(*args, **kwargs):
    """
    Main entry point for the prompt API
    Returns the result of the prompt function
    """
    p = json.dumps(prompt(*args, **kwargs).data)
    # print(f"{Fore.RED}{p = }{Fore.RESET}")
    contracts.write_tempfile(*args, content=p, **kwargs)
    # with open("C:/Users/lars/python_venvs/api_prompt.log", "w", encoding='utf-8') as f:
    #     f.write(f"api_prompt.main: {p = }")
    # sys.stdout.write(f"{p}\n")
    # sys.stdout.flush()
    return p

if __name__ == "__main__":
    main()