"""
api_thought.py
"""

from colorama import Fore, Style, Back
from datetime import datetime
import pyperclip as pc
import re, pyttsx3

import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.thought import Thought


# After the existing imports at the top of the file
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

def thought(*args, api:str, verbose:int, **kwargs):
    """
    Display basic information about the system and configuration
    Returns a dictionary containing the information
    """
    thought = Thought(api, *args, verbose=verbose, **kwargs)
    play_sound("PROMPT")
    response = thought.think(*args, verbose=verbose, **kwargs)
    if response is not None:
        hlpp.pretty_prompt(response.get('response'), *args, verbose=1, **kwargs)
        copy_response(response.get('response'), *args, **kwargs)
        speak_response(response.get('response'))
        play_sound("RESPONSE")
    else:
        print(f"{Fore.RED}api_thought: No response!{Fore.RESET}")
        play_sound("ERROR")

def copy_response(response: str, *args, to_clipboard:bool=False, **kwargs):
    """
    Copy the relevant part of the response to the clipboard.
    The relevant part consists of code snippets within the provided markdown response.
    Code is indicated by triple backticks, like so:```code```
    """
    if to_clipboard:
        # we use re to get the code snippets
        import re
        # Add a regular expression pattern to match code snippets
        pattern = r'```.*```'
        code_matches, code_snippets = re.findall(pattern, response, re.DOTALL), []
        # Copy each code snippet to the clipboard
        if code_matches:
            for snippet in code_matches:
                code_snippets.append(snippet)
            pc.copy("\n|\n".join(code_snippets))
        else:
            pc.copy(f"No code snippets found in response: \n{response}")
    else:
        pc.copy(f"{to_clipboard = }")

# After other functions and before main(), define play_sound
def play_sound(status: str):
    """
    Plays a short acoustic signal based on the given status.
    Args:
        status: (str) One of ["LOADED", "START", "STOP"].
    """
    if SOUND_AVAILABLE:
        if status == "PROMPT":
            winsound.Beep(600, 150)   # Lower pitch
            winsound.Beep(1000, 150)  # Higher pitch
        elif status == "RESPONSE":
            winsound.Beep(1000, 150)  # Higher pitch
            winsound.Beep(800, 150)   # Lower pitch
            winsound.Beep(600, 150)   # Lower pitch
        elif status == "ERROR":
            winsound.Beep(200, 550)

def speak_response(text: str):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def main(*args, **kwargs):
    """
    Main entry point for the thought API
    Returns the result of the thought function
    """
    return thought(*args, **kwargs)


if __name__ == "__main__":
    main()
