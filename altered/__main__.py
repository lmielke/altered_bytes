"""
    __main__.py
    Entry point for altered shell calls 
    ###################################################################################
    
    __main__.py imports the api module from altered >> apiModule.py
                and runs it
                api is provided as first positional argument

    ###################################################################################
    
    for user info runs: 
        python -m altered info
    above cmd is identical to
        python -m altered.info


"""

import colorama as color
from colorama import Fore, Style, Back
import importlib, os

import altered.settings as sts
import altered.arguments as arguments
import altered.contracts as contracts
from altered.hlp_directories import set_workdir


def runable(*args, api, **kwargs):
    """
    imports api as a package
    returns the runable result
    """
    if not api.startswith('api_'):
        api = f"api_{api}"
    if not os.path.exists(os.path.join(sts.package_dir, f"{api}.py")):
        raise FileNotFoundError(
                                    f"{Fore.RED}api {api} not found in{Fore.RESET} "
                                    f"{sts.package_dir}"
                                )
    return importlib.import_module(f"altered.{api}")

@sts.logs_timeit.timed("__main__.main")
def main(*args, **kwargs):
    """
    to runable from shell these arguments are passed in
    runs api if legidemit and prints outputs
    """
    kwargs = arguments.mk_args()
    # get workdir if provided
    kwargs.update(set_workdir(*args, **kwargs))
    # kwargs are vakidated against enforced contract
    kwargs = contracts.checks(*args, **kwargs)
    # the imported api runable package is executed
    if kwargs.get("api") == "help":
        print(  f"{Fore.YELLOW}__main__:{Fore.RESET} "
                f"For parameter and package info, run: 'alter info'")
    else:
        out = runable(*args, **kwargs).main(*args, **kwargs)
        return out


if __name__ == "__main__":
    main()
