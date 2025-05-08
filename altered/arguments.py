"""
Command-line argument parser for the altered_bytes package.
Handles API selection and various configuration parameters.

Usage:
    alter api_name [options]

Example:
    alter thought -v 1 -i sys_info_ops sys_info_usr -p pg_imports pg_requirements pg_tree 
    -n 3 -w api_prompt -r settings.* -u git_diff user_act ps_hist
"""
import argparse
import colorama as color
from colorama import Fore, Style, Back


def get_parser() -> argparse.ArgumentParser:
    """
    Create and configure command-line argument parser for altered_bytes.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Run altered_bytes APIs with configurable parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        "api",
        help=(  f"Name of the API module to run "
                f"(api_[{Fore.YELLOW}api{Fore.RESET}].py must exist in altered package)"
                f"\n{Fore.YELLOW}NOTE:{Fore.RESET} "
                f"For extended parameter and package info run: 'alter info'"
                ),
    )

    # Optional arguments
    parser.add_argument(
        "-al", "--alias",
        type=str,
        default='l3.2_1',
        help="Model (i.e. l3.2) and Server (i.e. 1) alias to use. (default: l3.2_1)"
    )


    parser.add_argument(
        "-tc", "--tool_choice",
        type=str,
        default='none',
        help=("Tool-choice: 'none', 'auto', or 'my_func_name'")
        )

    # System information options
    parser.add_argument(
        "-si", "--sys_info",
        nargs='*',
        type=str,
        default=[],
        help="Host system technical info options (e.g., -i sys_info_ops sys_info_usr)"
    )

    # Package information options
    parser.add_argument(
        "-pi", "--package_info",
        nargs='*',
        type=str,
        default=[],
        help="Host package info options (e.g., -p pg_imports pg_requirements)"
    )

    # User activity options
    parser.add_argument(
        "-ui", "--user_info",
        nargs='*',
        type=str,
        default=[],
        help="User activity info options (e.g., -u git_diff user_act ps_hist)"
    )

    # File handling options
    parser.add_argument(
        "-wf", "--work_file_name",
        type=str,
        help="Current workfile (root file for package import graph)"
    )
    # user question, comment
    parser.add_argument(
        "-up", "--user_prompt",
        type=str,
        help="user question or problem to solve"
    )

    # deliverable
    parser.add_argument(
        "-dl", "--deliverable_path",
        type=str,
        help="path to the deliverable"
    )

    # selection
    parser.add_argument(
        "-ds", "--selection",
        type=str,
        help="selected point of interest and deliverable"
    )
    # application, some application (sublime) require special behavior (allowerd chars)
    parser.add_argument(
        "-ap", "--application",
        type=str,
        default="powershell",
        help="calling application, sublime, powershell, ect."
    )

    parser.add_argument(
        "-rx", "--file_match_regex",
        type=str,
        default=None,
        help="Regex pattern to match desired file names (e.g., 'api_.*.py')"
    )

    # Behavior control options
    parser.add_argument(
        "-na", "--num_activities",
        type=int,
        default=0,
        nargs="?",
        const=1,
        help="Number of activities to list (default: 0)"
    )

    parser.add_argument(
        "-v", "--verbose",
        type=int,
        default=0,
        nargs="?",
        const=1,
        choices=[0, 1, 2, 3],
        help="Verbosity level (0: silent, 1: user, 2: simple debug, 3: detailed debug)"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Run without confirmation prompts"
    )

    parser.add_argument(
        "-cl", "--to_clipboard",
        action="store_true",
        help="Copy response to clipboard"
    )

    return parser

def mk_args() -> argparse.Namespace:
    """
    Parse command-line arguments for altered_bytes.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = get_parser()
    return parser.parse_args()
