"""
    pararses altered arguments and keyword arguments
    args are provided by a function call to mk_args()
    
    RUN like:
    import altered.arguments
    kwargs.updeate(arguments.mk_args().__dict__)
"""
import argparse
from typing import Dict


def mk_args():
    parser = argparse.ArgumentParser(description="run: python -m altered info")
    parser.add_argument(
                            "api", 
                            metavar="api", nargs=None, 
                            help=(
                                    f""
                                    f"see altered.apis"
                                )
                        )

    parser.add_argument(
        "-a",
        "--alias",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default='l3.2_1',
        help=(f"Server and model to use."),
    )

    parser.add_argument(
        "-s",
        "--sys_info",
        required=False,
        nargs='*',  # Allows multiple arguments as a list
        type=str,
        default=[],
        help=(  f"Host system technical infos. Provide multiple options "
                f"like: -s sys_info_ops sys_info_usr"
                ),
    )

    parser.add_argument(
        "-p",
        "--package_info",
        required=False,
        nargs='*',  # Allows multiple arguments as a list
        type=str,
        default=[],
        help=(  f"Host package infos. Provide multiple options "
                f"like: -p pg_imports pg_requirements"
                ),
    )

    parser.add_argument(
        "-u",
        "--user_info",
        required=False,
        nargs='*',  # Allows multiple arguments as a list
        type=str,
        default=[],
        help=(  f"User activity infos. Provide multiple options "
                f"like: -u git_diff user_act chat_hist"
                ),
    )

    parser.add_argument(
        "-g",
        "--work_file_name",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=None,
        help=(f"Root file for building the package import graph."),
    )

    parser.add_argument(
        "-r",
        "--file_match_regex",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=None,
        help=(f"Regex to match a desired file name i.e. api_.*.py ."),
    )

    parser.add_argument(
        "-n",
        "--num_activities",
        required=False,
        nargs="?",
        const=1,
        type=int,
        default=0,
        help="Number of activities to list.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        nargs="?",
        const=1,
        type=int,
        default=0,
        help="0:silent, 1:user, 2:debug",
    )

    parser.add_argument(
        "-y",
        "--yes",
        required=False,
        nargs="?",
        const=1,
        type=bool,
        default=False,
        help="run without confirm, not used",
    )

    return parser.parse_args()



def get_required_flags(parser: argparse.ArgumentParser) -> Dict[str, bool]:
    """
    Extracts the 'required' flag for each argument from an argparse.ArgumentParser object.

    Args:
        parser (argparse.ArgumentParser): The parser to extract required flags from.

    Returns:
        Dict[str, bool]: A dictionary with argument names as keys and their 'required' status as values.
    """
    required_flags = {}
    for action in parser._actions:
        if isinstance(action, argparse._StoreAction):
            # For positional arguments, the 'required' attribute is not explicitly set,
            # but they are required by default.
            is_required = getattr(action, 'required', True) if action.option_strings == [] else action.required
            # Option strings is a list of option strings (e.g., '-f', '--foo').
            for option_string in action.option_strings:
                required_flags[option_string] = is_required
            if not action.option_strings: # For positional arguments
                required_flags[action.dest] = is_required
    return required_flags

if __name__ == "__main__":
    parser = mk_args()
    required_flags = get_required_flags(parser)
    print(required_flags)
