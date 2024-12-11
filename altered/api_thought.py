"""
api_thought.py
"""

import colorama as color
from datetime import datetime

import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.thought import Thought

color.init()
def thought(*args, api:str, verbose:int, **kwargs):
    """
    Display basic information about the system and configuration
    Returns a dictionary containing the information
    """
    thought = Thought(api, *args, verbose=verbose, **kwargs)
    response = thought.think(*args, verbose=verbose, **kwargs)
    hlpp.pretty_prompt(response.get('response'), *args, verbose=1, **kwargs)

def main(*args, **kwargs):
    """
    Main entry point for the thought API
    Returns the result of the thought function
    """
    return thought(*args, **kwargs)

if __name__ == "__main__":
    main()
