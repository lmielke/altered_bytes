"""
api_prompt.py
"""

from colorama import Fore, Style
from datetime import datetime
import json
import sys

# package imports
import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.prompt import Prompt

def prompt(*args, api:str, **kwargs):
    """
    Display basic information about the system and configuration
    Returns a dictionary containing the information
    """
    return Prompt(api, *args, **kwargs)(*args, **kwargs)
    # hlpp.pretty_prompt(prompt.data, *args, verbose=verbose, **kwargs)

def main(*args, **kwargs):
    """
    Main entry point for the prompt API
    Returns the result of the prompt function
    """
    p = json.dumps(prompt(*args, **kwargs).data)
    sys.stdout.write(f"{p}\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()