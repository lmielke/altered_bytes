"""
prompt.py

"""
import os, yaml
import altered.settings as sts
from colorama import Fore, Style
from altered.prompt_strategies import Strategy
from altered.yml_parser import YmlParser

class UserPrompt:

    default_prompt_str = 'Want to add a user_prompt ?'

    def __init__(self, *args, name:str=None, **kwargs):
        self.name = name
        self.prompt_str = None
        self.user_prompt = None
        self.context = {}

    def __call__(self, *args, **kwargs):
        self.get_user_prompt(*args, **kwargs)
        return self.mk_context(*args, **kwargs)

    def mk_context(self, *args, **kwargs):
        self.context = {
                        'name': self.name,
                        'prompt_str': self.prompt_str,
                        'user_prompt': self.user_prompt,
        }
        return self.context

    def get_prompt_str(self, *args, prompt_str:str='', **kwargs):
        if not prompt_str:
            return self.default_prompt_str
        else:
            self.prompt_str = prompt_str
        return self.prompt_str
        
    def get_user_prompt(self, *args, user_prompt:str=None, **kwargs) -> str:
        # user_prompt is provided as an non-empty string and will be used
        if user_prompt:
            self.user_prompt = user_prompt
        # user_prompt is not provided or specifically set to None
        elif user_prompt is None:
            pass
        # user_prompt is provided as an empty string which triggers the input action
        elif not user_prompt:
            prompt_str = f"{self.get_prompt_str(*args, **kwargs)}\n"
            print(f"{Fore.YELLOW}{prompt_str}{Fore.RESET}")
            self.user_prompt = input(f"\tYou: ").strip()
            if not self.user_prompt.strip():
                print(f"No user_prompt provided: setting to None")
                self.user_prompt = None
        return self.user_prompt
