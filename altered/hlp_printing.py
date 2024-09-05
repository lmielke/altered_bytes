"""
hlp_printing.py
"""
import re
from colorama import Fore, Style
import altered.settings as sts
from textwrap import wrap as tw

def wrap_text(text:str, *args, max_chars:int=sts.table_max_chars, **kwargs):
    if type(text) == str and len(text) > max_chars:
        wrapped = ''
        for line in text.split('\n'):
            if len(line) > max_chars:
                line = '\n'.join(tw(line, max_chars))
            wrapped += f"\n{line}"
        return wrapped
    return text


def pretty_prompt(prompt:str, *args, verbose:int=0, **kwargs) -> str:
    prompt = re.sub(r'<user_prompt>\s*</user_prompt>', '', prompt, flags=re.MULTILINE)
    if verbose >= 2:
        # we replace the <tags> in prompt with colorized tags
        p = prompt.replace('context>', f"{Fore.BLUE}context>{Fore.RESET}")
        p = p.replace('rag_db_matches>', f"{Fore.GREEN}rag_db_matches>{Fore.RESET}")
        p = p.replace('user_prompt>', f"{Fore.YELLOW}user_prompt>{Fore.RESET}")
        p = p.replace('previous_responses>', f"{Fore.CYAN}previous_responses>{Fore.RESET}")
        p = p.replace('INST>', f"{Fore.CYAN}INST>{Fore.RESET}")
        print(f"\n\n{Fore.CYAN}# NEXT FAST_PROMPT:{Fore.RESET} \n{p}")


