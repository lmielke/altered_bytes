"""
Command-line argument parser for the altered_bytes package.
Handles API selection and various configuration parameters.

Usage:
    alter api [options]

Example:
    alter thought -v 1 -i sys_info_ops sys_info_usr -p pg_imports pg_requirements pg_tree 
    -n 3 -w api_prompt -r settings.* -u git_diff user_act ps_hist
"""
import argparse
import colorama as color
from colorama import Fore, Style, Back
import yaml
import os

import altered.settings as sts


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
        # Shorter help text for 'api'
        help=(f"API module to run (e.g., 'thought'). For details: 'alter info'. \n"
              f"(api_[{Fore.YELLOW}api{Fore.RESET}].py must exist)"
              ) 
    )

    parser.add_argument(
        "-k", "--kwargs_defaults",
        type=str,
        default=None, 
        # Shorter help text
        help="YAML file in resources/kwargs_defaults for defaults (e.g., 'sublime')."
    )

    # Optional arguments
    parser.add_argument(
        "-al", "--alias",
        type=str,
        default=None,
        # Shorter help text
        help="Model & Server alias (e.g., l3.2_1). Default: l3.2_1."
    )

    parser.add_argument(
        "-tc", "--tool_choice",
        type=str,
        default='none',
        help="Tool-choice: 'none', 'auto', or 'my_func_name'." # Already short
        )

    parser.add_argument(
        "-si", "--sys_info",
        nargs='*',
        type=str,
        default=[],
        # Shorter help text
        help="Host system technical info options (e.g., sys_info_usr)."
    )

    parser.add_argument(
        "-pi", "--package_info",
        nargs='*',
        type=str,
        default=[],
        # Shorter help text
        help="Package info options (pg_requirements, pg_imports, pg_tree)."
    )

    parser.add_argument(
        "-ui", "--user_info",
        nargs='*',
        type=str,
        default=[],
        # Shorter help text
        help="User activity info options (e.g., git_diff)."
    )

    parser.add_argument(
        "-wf", "--work_file_name",
        type=str,
        # Shorter help text
        help="Current workfile (root for package import graph)."
    )
    parser.add_argument(
        "-wd", "--work_dir",
        type=str,
        # Shorter help text
        help="Current work_dir."
    )
    parser.add_argument(
        "-up", "--user_prompt",
        type=str,
        help="User question or problem to solve." # Already short
    )
    parser.add_argument(
        "-uf", "--up_file",
        type=str,
        help="User question as file path." # Already short
    )
    
    parser.add_argument(
        "-dl", "--deliverable_path",
        type=str,
        help="Path to the deliverable." # Already short
    )

    parser.add_argument(
        "-ds", "--selection",
        type=str,
        help="Selected point of interest and deliverable." # Already short
    )
    parser.add_argument(
        "-ap", "--application",
        type=str,
        default="powershell",
        help="Calling application (e.g., sublime, powershell, etc.)." # Fixed typo
    )

    parser.add_argument(
        "-rx", "--file_match_regex",
        type=str,
        default=None,
        # Shorter help text
        help="Regex to match file names (e.g., 'api_.*.py')."
    )

    parser.add_argument(
        "-na", "--num_activities",
        type=int,
        default=0,
        nargs="?",
        const=1,
        help="Number of activities to list. Default: 0." # Slightly shorter
    )

    parser.add_argument(
        "-v", "--verbose",
        type=int,
        default=0,
        nargs="?", 
        const=1,   
        choices=[0, 1, 2, 3, 4, 5, 6],
        # Shorter help text
        help="Verbosity level (0-3). 0=silent, 3=detailed."
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Run without confirmation prompts." # Already short
    )

    parser.add_argument(
        "-cl", "--to_clipboard",
        action="store_true",
        help="Copy response to clipboard." # Already short
    )

    return parser

def mk_args() -> dict: 
    """
    Parse command-line arguments for altered_bytes.

    Returns:
        dict: Parsed command-line arguments as a dictionary.
              YAML values will overwrite CLI/code defaults.
              Will "fail fast" if YAML is missing or faulty.
    """
    return get_parser().parse_args().__dict__
