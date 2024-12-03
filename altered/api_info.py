"""
api_info.py
"""

import colorama as color
from datetime import datetime

import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.prompt import Prompt

color.init()
def info(*args, api:str, verbose:int, alias:str, **kwargs):
    """
    Display basic information about the system and configuration
    Returns a dictionary containing the information
    """
    prompt = Prompt(api, *args, **kwargs)(*args, **kwargs)
    hlpp.pretty_prompt(prompt.data, *args, verbose=2, **kwargs)

def main(*args, **kwargs):
    """
    Main entry point for the info API
    Returns the result of the info function
    """
    return info(*args, **kwargs)

if __name__ == "__main__":
    main()