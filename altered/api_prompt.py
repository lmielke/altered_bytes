"""
api_prompt.py
"""

from datetime import datetime
import json
import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.prompt import Prompt
from colorama import Fore, Style

def prompt(*args, api:str, verbose:int, **kwargs):
    """
    Display basic information about the system and configuration
    Returns a dictionary containing the information
    """
    return Prompt(api, *args, verbose=verbose, **kwargs)(*args, verbose=verbose, **kwargs)
    # hlpp.pretty_prompt(prompt.data, *args, verbose=verbose, **kwargs)

def main(*args, **kwargs):
    """
    Main entry point for the prompt API
    Returns the result of the prompt function
    """
    # return json.dumps(prompt(*args, **kwargs).data)
    print("Test")

if __name__ == "__main__":
    main()