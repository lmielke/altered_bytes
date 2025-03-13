import argparse, os, subprocess
from typing import List, Dict
from tabulate import tabulate
from colorama import Fore, Style, Back
import altered.arguments as arguments

def get_argument_details(parser: argparse.ArgumentParser) -> List[Dict[str, str]]:
    """
    Extract detailed information for each argument from the parser.
    Args:
        parser (argparse.ArgumentParser): Configured argument parser
    Returns:
        List[Dict[str, str]]: List of dictionaries, each containing details of an argument
    """
    argument_details = []
    for action in parser._actions:
        # Extracting details for each argument
        arg_info = {
            "Name": action.dest if action.dest else "",
            "Alias": ", ".join(action.option_strings) if action.option_strings else "",
            "Required": "Yes" if action.required else "No",
            "Type": action.type.__name__ if action.type else "str",
            "Default": str(action.default) if action.default is not None else "None",
            "Help": action.help or "No description"
        }
        argument_details.append(arg_info)
    return argument_details

def display_argument_info(*args, **kwargs):
    """
    Display argument information in a tabulate table.
    """
    # Create the parser using get_parser to get all defined arguments
    argument_parser = arguments.get_parser()  # This will provide the argument parser object
    # Extract argument details
    argument_details = get_argument_details(argument_parser)
    # Convert argument details to a list of lists for tabulate
    argument_details_list = [[  arg_info["Name"],
                                arg_info["Alias"],
                                arg_info["Required"],
                                arg_info["Type"],
                                arg_info["Default"], 
                                arg_info["Help"]] for arg_info in argument_details]
    # Display the table using tabulate
    headers = ["Name", "Alias", "Required", "Type", "Default", "Help"]
    print(tabulate(argument_details_list, headers=headers, tablefmt="grid"))

def check_environment_variables(*args, **kwargs):
    print(f"\n{Fore.WHITE}Environment Variables:{Fore.RESET}")
    if os.getenv('altered_bytes'):
        print(f"{Fore.GREEN}$env:altered_bytes: {Fore.RESET}{os.getenv('altered_bytes')}")
    else:
        print(  
                f"{Fore.RED}ERROR: altered_bytes env var not found."
                f"$env:altered_bytes: {os.getenv('altered_bytes')}{Fore.RESET}"
                f"Set altered_bytes env var to {sts.project_dir = }"
                )

def ping_altered_server(*args, **kwargs) -> str | None:
    """
    Pings the altered server to check if it is running.
    
    Returns:
        str: The server's response if successful.
        None: If the server is unresponsive or an error occurs.
    """
    address = 'localhost:5555/ping'
    try:
        result = subprocess.run(['curl', address], timeout=3, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(
                f"{Fore.RED}Error pinging server:{Fore.RESET} "
                f"{result.stderr.strip() or 'Unknown error'}"
            )
            return None
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}Server unresponsive (timeout):{Fore.RESET} {address}")
        return None
    except Exception as e:
        e_str = f"{e}".replace(address, f"{Fore.YELLOW}{address}{Fore.RESET}")
        print(f"{Fore.RED}Server unresponsive or not running:{Fore.RESET} {e_str}")
        return None

def call_commands(*args, **kwargs):
    """
    Prints alter call commands as part of info
    """
    msg = f"""alter thought -si sys_info_ops sys_info_usr -pi pg_requirements -na 3 -wf api_prompt -rx "None" -up "Help me solving my problem!" -dl "{__file__}" -v 3 -al l3.2_0"""
    print(f"{Fore.BLUE}EXAMPLES:{Fore.RESET}")
    print(f"{Fore.BLUE}\t-{msg}{Fore.RESET}")
    msg = msg.replace('thought', 'prompt')
    print(f"{Fore.BLUE}\t-{msg}{Fore.RESET}")

def main(*args, **kwargs):
    """
    Main function to display argument information.
    """
    display_argument_info(*args, **kwargs)
    check_environment_variables(*args, **kwargs)
    call_commands(*args, **kwargs)
    print(f"{Fore.GREEN}{ping_altered_server()}{Fore.RESET}")

if __name__ == "__main__":
    main()
