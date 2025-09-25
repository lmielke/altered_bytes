# contracts.py
import importlib, os, re, sys, yaml
from datetime import datetime as dt
from colorama import Fore, Style
from dotenv import load_dotenv
import pyttsx3

import altered.settings as sts
import altered.arguments as arguments
import altered.hlp_printing as hlpp
from altered.hlp_directories import normalize_path as normpath
# from altered.hlp_directories import set_workdir
from altered.hlp_dir_context import DirContext


def checks(*args, verbose:int=0, **kwargs):
    kwargs['verbose'] = verbose
    kwargs.update(get_kwargs_defaults(*args, **kwargs))
    kwargs.update(read_tempfile(*args, **kwargs))
    kwargs = clean_kwargs(*args, **kwargs)
    kwargs = prep_sys_infos(*args, **kwargs)
    kwargs = prep_user_info(*args, **kwargs)
    kwargs.update(get_package_data(*args, **kwargs))
    kwargs.update(clean_paths(*args, **kwargs))
    kwargs = prep_package_info(*args, **kwargs)
    kwargs.update(get_model_alias(*args, **kwargs))
    check_env_vars(*args, **kwargs)
    # check_req_kwargs(*args, **kwargs)
    if verbose:
        hlpp.pretty_dict('contracts.checks.kwargs', kwargs, *args, **kwargs)
    return kwargs

def get_package_data(*args, work_dir:str=None, **kwargs) -> dict:
    """
    Uses work_dir or cwd to detect package information such as project_dir, package_dir, ect.
    """
    work_dir = os.path.abspath(work_dir if work_dir is not None else os.getcwd())
    # traverses the directory structure to find project and package directories
    ctx = DirContext()(path=work_dir).__dict__
    # we only return a subset of the context information
    obj_names = {'pr_name', 'pg_name', 'work_dir', 'project_dir', 'package_dir', 'is_package'}
    pg_objs = {k: v for k, v in ctx.items() if k in obj_names}
    return pg_objs

def clean_paths(*args, **kwargs) -> dict:
    """
    WHY: Normalize *_dir/*_path and resolve missing files if path doesn't exist.
    """
    normalizeds = {}
    for n, v in kwargs.items():
        if isinstance(v, str) and any(t in n for t in {"_dir", "_path"}):
            normalizeds[n] = normpath(v, *args, **kwargs)
    return normalizeds

def write_tempfile(*args, api: str, content: str, up_file: str = None, **kwargs):
    """
    Writes the generated content JSON back to the original up_file, if provided.
    """
    # with open("C:/Users/lars/python_venvs/write_tempfile.log", 'w', encoding='utf-8') as f:
    #     f.write(f"api: {api}\ncontent: {content}\n{up_file = }")
    if not up_file:
        return  # Skip if no output path is specified
    up_file = normpath(up_file, *args, **kwargs)
    out_str = f"\n{api}_response:\n{content.strip()}\n"
    try:
        with open(up_file, 'a', encoding='utf-8') as f:
            f.write(out_str)
    except Exception as e:
        print(f"{Fore.RED}Failed to write content to file {up_file}: {e}{Fore.RESET}")

def read_tempfile(*args, user_prompt:str='', up_file:str=None, **kwargs) -> str:
    # user_promt might come as None from arguments
    user_prompt = '' if user_prompt is None else user_prompt
    if up_file is not None:
        up_file = normpath(up_file, *args, **kwargs)
        if not os.path.exists(up_file):
            raise FileNotFoundError(f"{Fore.RED}temp file {up_file} not found!{Fore.RESET}")
        with open(up_file, 'r', encoding='utf-8', errors='replace') as f:
            user_prompt = f"{f.read()}\n" + user_prompt
    return {'user_prompt': user_prompt.strip()}

def get_model_alias(*args, alias:str=None, **kwargs):
    if alias is None:
        # get the model alias from environment variable, if no model is found here
        # it will be set by model_params.SingleModelParams (see models_servers.yml)
        alias = os.environ.get('model')
    return {'alias': alias,}

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

def get_kwargs_defaults(*args, kwargs_defaults:str=None, verbose:int=0, **kwargs):
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
        if loaded.get('verbose') < verbose:
            loaded['verbose'] = verbose
        return loaded
    except FileNotFoundError:
        print(f"{Fore.RED}ERROR: {kwargs_defaults_file} not found!{Fore.RESET}")
        return {}

def check_env_vars(*args, verbose:int=0, **kwargs):
    """
    Some processes like pm2 run the application without environment variables.
    This function checks if the required environment variables are set.
    If not it adds them by loading the .env file.
    """
    if os.environ.get('pg_alias') is None:
        env_file = os.path.join(sts.project_dir, ".env")
        load_dotenv(env_file)
    if verbose:
        vars = {k: os.environ.get(k) for k in {'pg_alias', 'port'}}
        hlpp.pretty_dict('contracts.check_env_vars', vars, *args, **kwargs)
        # _speak_message(f"Contract set port {vars.get('port')}!")

def _speak_message(message: str, *args, **kwargs):
    """Uses pyttsx3 to speak a given message."""
    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print(f"Text-to-speech failed: {e}")
