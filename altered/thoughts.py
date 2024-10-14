"""
thought.py
This class orchestrates the communication between the user and the AI assistant.
It stores and manages the thought history and creates the thought message for the next prompt and
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
from altered.thought import Thought


class Thoughts(Thought):

    exit_terms = {'/bye', '/quit'}
    roles = ('user', 'assistant')
    # default_data_dir handles where table data are stored and loaded
    default_thoughts_dir = os.path.join(sts.resources_dir, 'data')


    def __init__(self, name:str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        # initial user_promt provided by the user
        self.running = False
        self.init_prompt = None
        # Data represents the thought data structure, where each line is a thought element
        self.data = Data(*args, name=self.name, **kwargs)
        self.data.show(verbose=2)

    def run(self, *args, **kwargs):
        # First we create the inital user_promt to run the thought
        self.prep_thoughts(*args, **kwargs)
        # the thoughts loop starts here
        while self.running:
            self.r = self.think(*args, **kwargs)
            self.append(*args, **kwargs)
            self.show(*args, **kwargs)
        # exit uses /bye or /quit
        print(f"{Fore.YELLOW}Thoughts ended{Fore.RESET}")
        self.data.save_to_disk(*args, **kwargs)

    def prep_thoughts(self, *args, user_prompt:str, role:str='user', **kwargs):
        self.running = True
        self.init_prompt = {'role': role, 'content': user_prompt}

    def append(self, *args, **kwargs):
        for role in self.roles:
            self.data.append(self.mk_data_record(*args, role=role, **kwargs))
        print(f"{Fore.GREEN}{Style.BRIGHT}Thoughts.think {Style.RESET_ALL}")

    def mk_data_record(self, *args, role:str, user_prompt:str, **kwargs):
        record = {c: str(self.r.get(c)) for c in self.data.columns}
        record.update({'role': role, 'name': self.name})
        # for role 'user' the prompt is displayed together with the answer/response
        if role == 'user':
            record['content'] = user_prompt
            record['prompt'] = hlpp.pretty_prompt(self.p.data)
        elif role == 'assistant':
            record['prompt'] = hlpp.pretty_prompt(record['prompt'])
        return record

    def mk_context(self, *args, **kwargs):
        context = {}
        # we add the thought history to the context
        history = self.data.mk_history(*args, **kwargs)
        if history:
            context['thought_history'] = history
        # we add the initial prompt to the context
        context['init_prompt'] = self.init_prompt
        return context

    def show(self, *args, verbose:int=0, **kwargs):
        if verbose <=1:
            os.system('cls')
        self.data.show(*args, verbose=verbose, **kwargs)

