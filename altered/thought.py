"""
chat.py
This class orchestrates the communication between the user and the AI assistant.
It creates the chat message for the next prompt and receives the response from the AI LLM.

Run like: pipenv run python -m altered.server_ollama_endpoint

"""

import os, re, sys, yaml
import random as rd
from tabulate import tabulate as tb
from colorama import Fore, Style

import altered.hlp_printing as hlpp
import altered.settings as sts
from altered.model_connect import SingleModelConnect
from altered.prompt import Prompt, Response
from altered.data import Data


class Thought:

    rd_div = 500


    def __init__(self, name:str, *args, **kwargs):
        # name of the chat can be used to locate/reference the saved chat
        self.name = re.sub(r'\W+', '_', name.lower())
        self.assi = SingleModelConnect(*args, **kwargs)
        # prompt constructor for LLM interaction
        self.prompt = Prompt(name, *args, **kwargs)
        self.response = Response(name, *args, **kwargs)

    def think(self, *args, **kwargs):
        # we call the prompt with history since all other context is handled by prompt
        self.p = self.prompt(*args, **kwargs)
        for p_cnt in range(5):
            # post calls the model and response handles post model cleanup
            self.r = self.response(self.post(p_cnt, *args, **kwargs), *args, **kwargs)
            if self.r: break
        else:
            print(f"{Fore.RED}Thought.think ERROR: {Fore.RESET}No valid response received!")
            return None
        return self.filters(*args, **kwargs)

    def filters(self, *args, r_filters:list=[], verbose:int=0, **kwargs):
        if not r_filters: 
            return self.r
        # we filter self.r by the keys provided in r_filters
        if type(r_filters) == str: r_filters = [r_filters]
        r = {k: self.r.get(k) for k in r_filters if k in self.r}
        if not r:
            if verbose:
                print(  f"{Fore.YELLOW}Thought.think WARNING, "
                        f"r_filters not in response dict:{Fore.RESET} {r_filters = }\n"
                        f"Returning self.r!"
                        )
            return self.r
        else:
            return r

    def post(self, p_cnt, *args, **kwargs):
        server_params = self.mk_model_params(*args, **kwargs)
        if p_cnt >= 2:
            pr = self.modify_prompt(p_cnt, *args, **kwargs)
        return self.assi.post([pr if p_cnt >= 2 else self.p.data], *args, **server_params)

    def modify_prompt(self, p_cnt, *args, verbose:int=0, **kwargs):
        """
        Modifies the existing prompt to force a alternative response
        """
        
        # Generate unique indices and sort them to ensure we traverse left-to-right
        idxs = sorted({rd.randint(0, len(self.p.data) - 1) 
                        for _ in range(max(5, len(self.p.data) // self.rd_div * p_cnt ))})
        if p_cnt >= 1 and verbose:
            print(  f"{Fore.YELLOW}Thought.post WARNING: {Fore.RESET}"
                    f"{p_cnt = }, modifying {idxs = }")
        # Use slicing to remove characters at the specified indices
        new_data, new_idx = [], 0
        for ix in idxs:
            new_data.append(self.p.data[new_idx:ix] + ' ')
            new_idx = ix
        new_data.append(self.p.data[new_idx:])  # Add the rest of the string
        # Join the slices into the final string
        return ''.join(new_data)

    def mk_model_params(self, *args, repeats:dict=sts.repeats, fmt:str=None, verbose:int=0, 
        **kwargs, ):
        # Construct model parameters specific to this Thought (see ModelConnect.get_params())
        server_params = {
                            'service_endpoint': 'get_generates',
                            'repeats': repeats,
                            'verbose': verbose,
                            'prompt_summary': self.p.context.get('prompt_summary'),
                        }
        ignore_fields = {'context',}
        server_params.update({k:vs for k, vs in kwargs.items() if not k in ignore_fields})
        server_params['fmt'] = self.p.fmt
        return server_params
