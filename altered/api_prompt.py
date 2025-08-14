"""
api_prompt.py
"""

from colorama import Fore, Style
from datetime import datetime
import os, json, sys

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
    contracts.write_tempfile(*args, content=p, **kwargs)
    sys.stdout.write(f"{p}\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()