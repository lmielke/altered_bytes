"""
thought.py
This class orchestrates the communication between the user and the AI assistant.
It creates the chat message for the next prompt and receives the response from the AI LLM.

Run like: pipenv run python -m altered.server_ollama_endpoint

"""

import os, re, sys, yaml
from datetime import datetime as dt
import random as rd
from tabulate import tabulate as tb
from colorama import Fore, Style

import altered.settings as sts
import altered.contracts as contracts
from altered.model_connect import SingleModelConnect
from altered.prompt import Prompt, Response
from typing import List, Dict, Any


class Thought:


    def __init__(self, name:str, *args, **kwargs):
        # name of the chat can be used to locate/reference the saved chat
        # with open('C:/temp/api_thought.log', 'a') as l: 
        #     l.write(f"\nThought1: \n{re.sub(r'([: .])', '-', str(dt.now()))}: \n{args = }\n{kwargs = }")
        self.name = re.sub(r'\W+', '_', name.lower())
        self.assi = SingleModelConnect(*args, **kwargs)
        # prompt constructor for LLM interaction
        self.prompt = Prompt(name, *args, **kwargs)
        self.response, self.last_response = Response(name, *args, **kwargs), None

    @sts.logs_timeit.timed("thought.Thought.think")
    def think(self, *args, **kwargs):
        # we call the prompt with history since all other context is handled by prompt
        self.p = self.prompt(*args, **kwargs)
        kwargs['num_predict'] = self.p.I.context.get('num_predict', kwargs.get('num_predict'))
        for self.p_cnt in range(1, 3):
            # post calls the model and response handles post model cleanup
            self.r = self.response(self.post(*args, **kwargs), *args, **kwargs)
            if self.r:
                self.last_response = self.r.get('content')
                self.prompt.log_prompts([self.last_response], 'Response', self.p_cnt, *args, **kwargs)
                break
            else:
                self.prompt.log_prompts(['Thought.think: No response.'], 'Response', self.p_cnt, *args, **kwargs)
        else:
            print(  f"{Fore.RED}Thought.think ERROR: {self.p_cnt}{Fore.RESET} "
                    f"No valid response received!")
            return None
        filtered = self.filters(*args, **kwargs)
        return filtered


    def filters(self, *args, r_filters:list=[], verbose:int=0, user_prompt:str=None, **kwargs
        ) -> dict:
        if not r_filters:
            self.r['user_prompt'] = self.p.user_prompt
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

    def post(self, *args, **kwargs):
        server_params = self.mk_model_params(*args, **kwargs)
        if self.p_cnt >= 2:
            pr = self.modify_prompt(*args, **kwargs)
        final_prompts = [pr if self.p_cnt >= 2 else self.p.data]
        self.prompt.log_prompts(final_prompts, 'Prompt', self.p_cnt, *args, **kwargs)
        # print(f"{Fore.YELLOW}Thought.post: {Fore.RESET}{final_prompts}\n\n{server_params}")
        return self.assi.post(final_prompts, *args, **server_params)

    def modify_prompt(self, *args, verbose:int=0, **kwargs):
        """
        Modifies the existing prompt to force a alternative response
        """
        # Generate unique indices and sort them to ensure we traverse left-to-right
        # 500 is a devider that reduces the amound of charactes changed in the text
        idxs = sorted({rd.randint(0, len(self.p.data) - 1) 
                        for _ in range(max(5, len(self.p.data) // 500 * self.p_cnt ))})
        if self.p_cnt >= 1 and verbose:
            print(  f"{Fore.YELLOW}Thought.post WARNING: {Fore.RESET}"
                    f"{self.p_cnt = }, modifying {idxs = }")
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
                    'num_predict': self.p.I.context.get('num_predict'),
                        }
        ignore_fields = {'context', 'num_predict', }
        server_params.update({k:vs for k, vs in kwargs.items() if not k in ignore_fields})
        server_params['fmt'] = self.p.fmt
        return server_params
