# contracts.py
import altered.settings as sts
import importlib, os, sys, yaml
import altered.arguments as arguments
from colorama import Fore, Style
import altered.hlp_printing as hlpp
from altered.hlp_directories import normalize_path as normpath



def checks(*args, verbose:int, **kwargs):
    kwargs['verbose'] = verbose
    kwargs = clean_kwargs(*args, **kwargs)
    kwargs = prep_sys_infos(*args, **kwargs)
    kwargs = prep_package_info(*args, **kwargs)
    kwargs = prep_user_info(*args, **kwargs)
    kwargs = clean_paths(*args, **kwargs)
    # check_req_kwargs(*args, **kwargs)
    if verbose:
        hlpp.pretty_dict('contracts.checks.kwargs', kwargs, *args, **kwargs)
    return kwargs


def clean_kwargs(*args, **kwargs):
    # kwargs might come from a LLM api and might be poluted with whitespaces ect.
    cleaned_kwargs = dict()
    for k, vs in kwargs.items():
        if isinstance(vs, str):
            cleaned_kwargs[k.strip()] = vs.strip().strip("'")
        else:
            cleaned_kwargs[k.strip()] = vs
    return cleaned_kwargs

def prep_sys_infos(*args, sys_info:list=None, **kwargs):
    preped_kwargs = dict(**kwargs)
    if sys_info:
        preped_kwargs['sys_info'] = True
        for info in sys_info:
            preped_kwargs[info] = True
    else:
        preped_kwargs['sys_info'] = False
    return preped_kwargs

def prep_package_info(*args, package_info:list=None, is_package:bool=None, **kwargs):
    """
    Unpacks package_info list into kwargs.
    For example {'package_info': ['pg_requirements', 'pg_imports', 'pg_tree']}
    """
    preped_kwargs = dict(**kwargs, is_package=is_package)
    if package_info and is_package:
        preped_kwargs['package_info'] = True
        for info in package_info:
            preped_kwargs[info] = True
    elif package_info and not is_package:
        if kwargs.get('verbose'):
            print(f"{Fore.YELLOW}WARNING: package_info provided, but is_package is False! "
                f"Only pg_tree is used!{Style.RESET_ALL}" )
        preped_kwargs['package_info'] = True
        if 'pg_tree' in package_info:
            preped_kwargs['pg_tree'] = True
    else:
        preped_kwargs['package_info'] = False
    return preped_kwargs

def prep_user_info(*args, user_info:list=None, **kwargs):
    preped_kwargs = dict(**kwargs)
    if user_info:
        preped_kwargs['user_info'] = True
        for info in user_info:
            preped_kwargs[info] = True
    else:
        preped_kwargs['user_info'] = False
    return preped_kwargs

def prep_file_match_regex(*args, file_match_regex:str=None, **kwargs):
    if file_match_regex is None or file_match_regex == 'None':
        file_match_regex = ""
    return dict(**kwargs, file_match_regex=file_match_regex)

def clean_paths(*args, **kwargs):
    """
    Loops over known path parameters in kwargs, expands user ('~') and
    environment variables (e.g., '%USERNAME%' or '$HOME'), and
    converts them to absolute, normalized paths.

    Returns the kwargs dictionary with path values updated.
    """
    KNOWN_PATH_KEYS = ['work_file_name', 'deliverable_path', 'work_dir', ]
    cleaned_kwargs = dict(**kwargs)  # Work on a copy
    for key in KNOWN_PATH_KEYS:
        if key in cleaned_kwargs:
            path_value = cleaned_kwargs[key]
            if isinstance(path_value, str) and path_value.strip(): # Process non-empty strings
                # 1. Expand environment variables (e.g., %VAR% on Windows, $VAR on Unix)
                #    This handles variables like %USERNAME%, %APPDATA%, $HOME, $USER, etc.
                expanded_vars_path = os.path.expandvars(path_value)
                # 2. Expand user component (e.g., ~ or ~user)
                expanded_user_path = os.path.expanduser(expanded_vars_path)
                # 3. Convert to an absolute path.
                #    Also normalizes path separators (e.g., converts '/' to '\' on Windows)
                #    and resolves components like '.' or '..'.
                absolute_path = os.path.abspath(expanded_user_path)
                cleaned_kwargs[key] = absolute_path
            # If path_value is None, an empty string after stripping, or not a string,
            # remains unchanged in cleaned_kwargs. This avoids errors with os.path functions.
    return cleaned_kwargs

def check_req_kwargs(*args, api:str, **kwargs):
    """
    from the api file we import "required_args" if avalilable and veryfy 
    the existence of minimum required arguments.
    """
    # here we create the import variable using importlib
    try:
        api_module = importlib.import_module(f"altered.api_{api}")
        if hasattr(api_module, 'required_args'):
            for kwarg in api_module.required_args:
                if kwargs.get(kwarg) is None:
                    raise ValueError(   f"\ncontracts.check_req_kwargs: "
                                        f"missing {kwarg = }"
                                        )
    except ImportError as e:
        print(f"{Fore.RED}ERROR: {e}{Style.RESET_ALL}")
        raise
    except ValueError as ve:
        print(f"{Fore.RED}ERROR: {ve}{Style.RESET_ALL}")
        raise

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


def get_up_from_file(*args, user_prompt:str=None, up_file:str=None, **kwargs) -> str:
    user_prompt = '' if user_prompt is None else user_prompt
    if up_file is not None:
        up_file = normpath(up_file, *args, **kwargs)
        if not os.path.exists(up_file):
            raise FileNotFoundError(f"{Fore.RED}File {up_file} does not exist!{Fore.RESET}")
        with open(up_file, 'r') as f:
            user_prompt += f"\n{f.read()}"
    return {'user_prompt': user_prompt.strip()}