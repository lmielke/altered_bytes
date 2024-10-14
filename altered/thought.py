"""
chat.py
This class orchestrates the communication between the user and the AI assistant.
It stores and manages the chat history and creates the chat message for the next prompt and
receives the response from the AI LLM. 

Run like: pipenv run python -m altered.pre_ollama_server

"""

import os, re, sys, yaml
from tabulate import tabulate as tb
from colorama import Fore, Style

import altered.hlp_printing as hlpp
import altered.settings as sts
from altered.model_connect import SingleModelConnect
from altered.prompt import Prompt, Response
from altered.data import Data


class Thought:

    def __init__(self, name:str, *args, **kwargs):
        # name of the chat can be used to locate/reference the saved chat
        self.name = re.sub(r'\W+', '_', name.lower())
        self.assi = SingleModelConnect(*args, **kwargs)
        # prompt constructor for LLM interaction
        self.prompt = Prompt(name, *args, **kwargs)
        self.response = Response(*args, **kwargs)

    def think(self, *args, **kwargs):
        # we call the prompt with history since all other context is handled by prompt
        self.p = self.prompt(*args, **kwargs, )
        # response handles post model cleanup
        self.r = self.response(self.post(*args, **kwargs), *args, **kwargs)
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

    def post(self, *args, **kwargs):
        server_params = self.mk_model_params(*args, **kwargs)
        # we post one or multiple user prompts to the AI model (repeats == num of prompt reps)
        return self.assi.post([self.p.data], *args, **server_params, )

    def mk_model_params(self, *args, repeats:dict=None, verbose:int=0, **kwargs, ):
        # Construct model parameters specific to this Thought (see ModelConnect.get_params())
        server_params = {
                            'service_endpoint': 'get_generates',
                            'repeats': repeats,
                            'verbose': verbose,
                            'prompt_summary': self.p.context.get('prompt_summary'),
                        }
        ignore_fields = {'context',}
        server_params.update({k:vs for k, vs in kwargs.items() if not k in ignore_fields})
        return server_params
