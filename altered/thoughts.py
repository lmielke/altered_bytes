"""
thougts.py
"""

"""
Handles RAG (Retrieval Augmented Generation) data for the agents.
"""

import getpass, hashlib, json, math, os, re, requests, shutil, time, yaml
import random as rd
from typing import Dict, Any, List, Union
import pandas as pd
import numpy as np
from numpy.linalg import norm as np_norm
pd.options.display.max_colwidth = 120
from datetime import datetime as dt
from tabulate import tabulate as tb
from colorama import Fore, Style

from altered.model_connect import ModelConnect
import altered.settings as sts


class QuickThought:
    """
    Example usage:
        self.assi = QuickThought(*args, model='llama3.1', **kwargs)
        self.assi('Why is the sky blue?', single_shot=True)
    """

    def __init__(self, *args, name:str=None, **kwargs):
        self.name = name if name else 'QuickThought'
        self.msgs = ModelConnect()
        self.last_msg, self.last_response = None, None


    def __call__(self, *args, **kwargs):
        return self.chat(*args, **kwargs)

    def chat(self, *args, **kwargs) -> str:
        """
        Chat with the model using the QuickThought method.
        
        Args:
            msg: The message to send to the model.
            single_shot: Whether to break the loop after one response.
        
        Returns:
            A response from the model based on the provided context.
        """
        self.prep_msg(*args, **kwargs)
        while True:
            

    def prep_msg(self, msg:str, *args, role:str='user', **kwargs) -> Any:
        """
        Prepare messages for the chat.
        
        Args:
            msg: The message to send.
            role: The role of the sender ('user' or 'assistant').
        
        Returns:
            None if the chat should continue, False if it should end.
        """
        if msg is None:
            msg = self.get_user_input(*args, **kwargs)
        if msg in self.bye:
            return False
        self.msgs.append(   {
                                'name': self.name,
                                'unique_name': None,
                                'content': msg,
                                'role': role,
                                'category': None,
                                'source': None,
                                'tools': None,
                                'hash': None,
                                'model': None,
                                'timestamp': dt.now().isoformat(),
                            }
        )
        return True

    def get_user_input(self, *args, **kwargs) -> str:
        print(f"{Fore.RED}Type your next prompt or exit with {self.bye}. {Fore.RESET}")
        msg = input(f'{getpass.getuser()}: ').strip()
        return msg

    def prep_prompt(self, *args, instruct:list=None, verbose:int=0, **kwargs) -> Dict[str, Any]:
        """
        Prepare the context dictionary for the API request.
        
        Returns:
            A dictionary containing the prompt and model configuration.
        """
        if instruct is None:
            # if no instruct is provided, we use the last message as instruction
            # all prior messages are treated as context
            context = '\n'.join([msg['content'] for msg in self.msgs[:-1]])
            user_prompt = ''
            instruction = f"{self.msgs[-1]['content']}"
        else:
            # if instruct is provided, we use the entire chat history as context
            context = '\n'.join([msg['content'] for msg in self.msgs[:-1]])
            user_prompt = f"{self.msgs[-1]['content']}"
            instruction = instruct
        # the prompt is made up of two sections 
        # context: contextual information to allow the instruction to be understood
        # instruction: question/problem statement to be solved by the model
        prompt =    (   
                        f"<context>\n"
                            f"{context}\n"
                        f"</context>\n"
                        f"\n"
                        f"<user_prompt>\n"
                            f"{user_prompt}\n"
                        f"</user_prompt>\n"
                        f"\n"
                        f"<INST>\n"
                            f"{instruction}\n"
                        f"</INST>\n"
                    ).strip().strip('\n')
        prompt = re.sub(r'<user_prompt>\s*</user_prompt>', '', prompt, flags=re.MULTILINE)
        if verbose >= 2:
            # we replace the <tags> in prompt with colorized tags
            p = prompt.replace('context>', f"{Fore.BLUE}context>{Fore.RESET}")
            p = p.replace('rag_db_matches>', f"{Fore.GREEN}rag_db_matches>{Fore.RESET}")
            p = p.replace('user_prompt>', f"{Fore.YELLOW}user_prompt>{Fore.RESET}")
            p = p.replace('previous_responses>', f"{Fore.CYAN}previous_responses>{Fore.RESET}")
            p = p.replace('INST>', f"{Fore.CYAN}INST>{Fore.RESET}")
            print(f"\n\n{Fore.CYAN}# NEXT FAST_PROMPT:{Fore.RESET} \n{p}")
        return prompt
