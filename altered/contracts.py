# contracts.py
import altered.settings as sts
import os, sys
import altered.arguments as arguments

import altered.hlp_printing as hlpp



def checks(*args, verbose:int, **kwargs):
    kwargs['verbose'] = verbose
    if verbose >= 2:
        print(f"contracts.checks.kwargs: {kwargs = }")
    kwargs = clean_kwargs(*args, **kwargs)
    kwargs = prep_sys_infos(*args, **kwargs)
    kwargs = prep_package_info(*args, **kwargs)
    kwargs = prep_user_info(*args, **kwargs)
    if verbose:
        hlpp.pretty_dict('contracts.checks.kwargs', kwargs, *args, **kwargs)
        print(f"contracts.checks.kwargs: \n{kwargs = }")
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

def prep_sys_infos(*args, sys_info:list, **kwargs):
    preped_kwargs = dict(**kwargs)
    if sys_info:
        preped_kwargs['sys_info'] = True
        for info in sys_info:
            preped_kwargs[info] = True
    else:
        preped_kwargs['sys_info'] = False
    return preped_kwargs

def prep_package_info(*args, package_info:list, **kwargs):
    preped_kwargs = dict(**kwargs)
    if package_info:
        preped_kwargs['package_info'] = True
        for info in package_info:
            preped_kwargs[info] = True
    else:
        preped_kwargs['package_info'] = False
    return preped_kwargs

def prep_user_info(*args, user_info:list, **kwargs):
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
