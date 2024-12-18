"""
api_thought.py
"""

from colorama import Fore, Style, Back
from datetime import datetime

import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.thought import Thought


def thought(*args, api:str, verbose:int, **kwargs):
    """
    Display basic information about the system and configuration
    Returns a dictionary containing the information
    """
    thought = Thought(api, *args, verbose=verbose, **kwargs)
    response = thought.think(*args, verbose=verbose, **kwargs)
    if response is not None:
        hlpp.pretty_prompt(response.get('response'), *args, verbose=1, **kwargs)
    else:
        print(f"{Fore.RED}api_thought: No response!{Fore.RESET}")

def main(*args, **kwargs):
    """
    Main entry point for the thought API
    Returns the result of the thought function
    """
    return thought(*args, **kwargs)

if __name__ == "__main__":
    main()
