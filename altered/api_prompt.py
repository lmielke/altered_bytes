"""
api_prompt.py
"""

from colorama import Fore, Style
from datetime import datetime
import os, json, sys, yaml

# package imports
import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.hlp_directories import normalize_path as normpath
from altered.prompt import Prompt

required_args = {'user_prompt',}

def prompt(*args, api:str, **kwargs):
    """
    Display basic information about the system and configuration
    Returns a dictionary containing the information
    """
    kwargs.update(get_kwargs_defaults(*args, **kwargs))
    return Prompt(api, *args, **kwargs)(*args, **kwargs)
    # hlpp.pretty_prompt(prompt.data, *args, verbose=verbose, **kwargs)

def get_kwargs_defaults(*args, kwargs_defaults:str=None, **kwargs):
    """
    Uses the kwargs_defaults string to return a dictionary of default values
    """
    if kwargs_defaults is None:
        return {}
    kwargs_defaults_file = os.path.join(sts.kwargs_defaults_dir, f"{kwargs_defaults}.yaml")
    try:
        with open(kwargs_defaults_file, 'r') as f:
            loaded = yaml.safe_load(f)
            for k, vs in loaded.items():
                if any({w in k for w in {'path', 'dir', 'file'}}):
                    loaded[k] = normpath(vs, *args, **kwargs)
            return loaded
    except FileNotFoundError:
        print(f"{Fore.RED}ERROR: {kwargs_defaults_file} not found!{Fore.RESET}")
        return {}

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