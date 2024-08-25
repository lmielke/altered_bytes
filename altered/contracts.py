# contracts.py
import altered.settings as sts
import altered.gp.models.openai.model_settings as gp_sts
import os, sys
import altered.arguments as arguments



def checks(*args, **kwargs):
    kwargs = clean_kwargs(*args, **kwargs)
    check_missing_kwargs(*args, **kwargs)
    kwargs.update(get_model(*args, **kwargs))
    adhog_chat_contracts(*args, **kwargs)
    return kwargs


def clean_kwargs(*args, **kwargs):
    # kwargs might come from a LLM api and might be poluted with whitespaces ect.
    cleaned_kwargs = {}
    for k, vs in kwargs.items():
        if isinstance(vs, str):
            cleaned_kwargs[k.strip()] = vs.strip().strip("'")
        else:
            cleaned_kwargs[k.strip()] = vs
    return cleaned_kwargs

def check_missing_kwargs(*args, api,  **kwargs):
    """
    Uses arguments to check if all required kwargs are provided
    """
    if api == 'clone':
        requireds = {
                        'new_pr_name': 'myhammerlib',
                        'new_pg_name': 'myhammer',
                        'new_alias': 'myham',
                        'tgt_dir': 'C:/temp',
                        }
    else:
        requireds = {}
    missings = set()
    for k, v in requireds.items():
        if k not in kwargs.keys():
            missings.add(k)
    if missings:
        print(f"{sts.RED}Missing required arguments: {missings}{sts.ST_RESET}")
        print(f"{sts.YELLOW}Required arguments are: {requireds}{sts.ST_RESET}")
        exit()

def get_model(*args, model:str, **kwargs):
    # print(f"{gp_sts.models.keys() = }")
    if model in gp_sts.models.keys():
        selected = {'model': gp_sts.models[model]}
    elif model in gp_sts.models.values():
        selected = {'model': model}
    elif model is None:
        selected = {'model': gp_sts.default_model}
    else:
        raise Exception(f"{sts.RED}Model {model} not found in gp_sts.models {sts.ST_RESET}")
    print(f"{sts.YELLOW}Model: {selected['model']}{sts.RESET}")
    return selected

def adhog_chat_contracts(*args, experts:list, **kwargs):
    if experts is None:
        experts = ' '.join([expert for expert in sts.skills.keys()])
        raise Exception(f"{sts.RED}No experts provided! Example: -e {experts} {sts.RESET}")
    else:
        return True