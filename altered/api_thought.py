"""
api_thought.py
"""

from colorama import Fore, Style, Back
from datetime import datetime as dt
import pyperclip as pc
import json, os, re, pyttsx3

import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.thought import Thought
import altered.contracts as contracts


@sts.logs_timeit.timed("api_thought.thought")
def thought(*args, api: str, verbose: int, application:str='powershell', **kwargs):
    """
    Main function to process a 'thought' using the given API and arguments.
    """
    application = 'powershell' if application is None else application.lower()
    try:
        # with open('C:/temp/api_thought.log', 'a') as l: 
        #     l.write(f"thought0:\n\n{re.sub(r'([: .])', '-', str(dt.now()))}: \n{args = }\n{kwargs = }")
        thought = Thought(api, *args, verbose=verbose, api=api, **kwargs)
        response = thought.think(*args, verbose=verbose, **kwargs)
        hlpp.play_sound('RESPONSE2')
        if response is None:
            msg = "ERROR: api_thought.thought: Response is None!"
            print(f"{Fore.RED}{msg}{Fore.RESET}")
            return msg
        elif not response.get('response'):
            msg = "ERROR: api_thought.thought: No model response in response dict!"
            print(f"{Fore.RED}{msg}{Fore.RESET}")
            return msg
        response_text = response.get('response', '').strip()
        code_blocks = copy_response(response_text, *args, **kwargs)
        log_path = os.path.join(sts.logs_dir, 'prompts', f"{sts.time_stamp()}_response.md" )
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log_response(response_text, log_path, *args, **kwargs)
        output_json = json.dumps(
                                    {
                                        'response': response.get('response'),
                                        'log_path': log_path,
                                    }, indent=4)
        if any([app in application.lower() for app in ['sublime', 'voice']]):
            print(f"\n{application} {output_json}")
            return output_json
        return response.get('response')
    except Exception as e:
        msg = f"ERROR: altered.api_thought.thought: {e}"
        print(f"{Fore.RED}{msg}{Fore.RESET}")
        return msg

def copy_response(response: str, *args, to_clipboard: bool = False, **kwargs):
    """
    Copy code snippets from a markdown response to the clipboard.
    Code is indicated by triple backticks, like so: ```code```
    Args:
        response: (str) The response string to process.
        to_clipboard: (bool) If True, copy found code blocks to clipboard.
    
    Returns:
        code_blocks: (list) A list of matched code snippets.
    """
    def get_code_blocks(text):
        # first we greedely select the widest backtick enclosure possible
        back_tick_match = re.search(r'\n```\s?[a-z]{0,20}\s?\n.*```', text, re.DOTALL)
        if not back_tick_match:
            return []
        else:
            back_tick_block = back_tick_match.group()
        code_block, markdown_block = False, False
        code_lines, code_blocks, block_cnt = '', [], 0
        # second we further split the backtick enclosure into code blocks
        for i, line in enumerate(back_tick_block.split('\n')):
            if re.search(r'^```[a-z]{3,20}', line):
                # this starts a new code or markdown block
                if 'markdown' in line:
                    markdown_block = True
                else:
                    block_cnt += 1
                    code_block, code_lines = True, f"block {block_cnt}:\n{line}"
            elif line.startswith('```'):
                # this ends a code or markdown block
                if markdown_block and not code_block:
                    markdown_block = False
                else:
                    # we finalize the code block and add the code block to the output list
                    code_blocks.append(code_lines + f"\n{line}\n")
                    code_block, code_lines = False, ''
            elif code_block:
                code_lines += f"\n{line}\n"
        if code_block:
            code_lines += f"\n```missing backticks correction\n"
        if markdown_block:
            code_lines += f"\n```missing backticks correction\n"
        return code_blocks
    if '```' in response:
        code_blocks = get_code_blocks(response)
    if '```markdown' in response and not code_blocks:
        code_blocks = get_code_blocks(response.replace('```markdown', '```unknown'))
    else:
        code_blocks = None
    if not code_blocks:
        code_blocks = f"No code blocks found in the response. \n{response = }"
    elif code_blocks and to_clipboard:
        # if to_clipboard is True, we copy the code blocks to the clipboard
        pc.copy('\n'.join(code_blocks))
    return code_blocks

def speak_response(response: str, code_blocks, *args, **kwargs):
    spoken = response
    for code_match in code_blocks:
        spoken = spoken.replace(code_match, '\nYou can find the code in your clipboard.\n')
    if len(spoken.split(' ')) <= 50 and not re.search(r'[=*]', spoken):
        engine = pyttsx3.init()
        engine.say(spoken)
        engine.runAndWait()

def log_response(response:str, log_path:str, *args, **kwargs):
    """
    Log the response to a file in the logs directory
    """
    with open(log_path, 'w') as f:
        f.write(response)

def open_log_file(log_path:str, *args, **kwargs):
    os.system(f"start notepad {log_path}")

def main(*args, **kwargs) -> str:
    """
    Main entry point for the thought API
    Returns the result of the thought function
    """
    kwargs.update(contracts.checks(*args, **kwargs))
    # with open(os.path.join(sts.logs_dir, 'server', 'api_thought_kwargs.log'), 'a') as f:
    #     f.write(f"\n\n{re.sub(r"([: .])", r"-" , str(dt.now()))}: \n{kwargs = }")
    r = thought(*args, **kwargs)
    # t = json.dumps(prompt(*args, **kwargs).data)
    contracts.write_tempfile(*args, content=r, **kwargs)
    return r


if __name__ == "__main__":
    main()
