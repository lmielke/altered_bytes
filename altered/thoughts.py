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
from altered.model_connect import ModelConnect
from altered.prompt import Prompt, Response
from altered.data import Data


class Chat:

    exit_terms = {'/bye', '/quit'}
    roles = ('user', 'assistant')
    # default_data_dir handles where table data are stored and loaded
    default_chats_dir = os.path.join(sts.resources_dir, 'data')


    def __init__(self, name:str, *args, **kwargs):
        # name of the chat can be used to locate/reference the saved chat
        self.name = re.sub(r'\W+', '_', name.lower())
        self.assi = ModelConnect(*args, **kwargs)
        # initial user_promt provided by the user
        self.running = False
        self.init_prompt = None
        # prompt constructor for LLM interaction
        self.prompt = Prompt(name, *args, **kwargs)
        self.response = Response(*args, **kwargs)
        # Data represents the chat data structure, where each line is a chat element
        self.data = Data(*args, name=self.name, **kwargs)

    def run(self, *args, **kwargs):
        # First we create the inital user_promt to run the chat
        # the chat loop starts here
        # self.mk_data_record(running, *args, **kwargs)
        self.prep_chat(*args, **kwargs)
        while self.running:
            self.running = self.next_chat_item(*args, **kwargs)
        # exit uses /bye or /quit
        print(f"{Fore.YELLOW}Chat ended{Fore.RESET}")
        self.data.save_to_disk(*args, **kwargs)

    def prep_chat(self, *args, user_prompt:str, role:str='user', **kwargs):
        self.running = True
        self.init_prompt = {'role': role, 'content': user_prompt}

    def next_chat_item(self, *args, **kwargs):
        # we call the prompt with history since all other context is handled by prompt
        self.p = self.prompt(*args, context=self.mk_context(*args, **kwargs), **kwargs, )
        # response handles post model cleanup
        self.r = self.response(self.post(*args, **kwargs), *args, **kwargs)
        # we create the next record to update the chat
        for role in self.roles:
            self.data.append(self.mk_data_record(*args, role=role, **kwargs))
        self.show(*args, **kwargs)

    def post(self, *args, **kwargs):
        server_params = self.mk_model_params(*args, **kwargs)
        # we post one or multiple user prompts to the AI model (repeats == num of prompt reps)
        return self.assi.post([self.p.data], *args, **server_params, )

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

    def mk_model_params(self, *args, repeats:int=1, 
                                    strat_templates:str=None, verbose:int=0, **kwargs,
        ):
        # Construct model parameters specific to this Chat (see ModelConnect.get_params())
        strat_templates =  ['agg_mean'] if repeats != 1 and strat_templates is None \
                                        else strat_templates
        server_params = {
                            'service_endpoint': 'get_generates',
                            'strat_templates': strat_templates,
                            'repeats': repeats,
                        }
        ignore_fields = {'context',}
        server_params.update({k:vs for k, vs in kwargs.items() if not k in ignore_fields})
        return server_params

    def mk_context(self, *args, **kwargs):
        context = {}
        # we add the chat history to the context
        history = self.data.mk_history(*args, **kwargs)
        if history:
            context['context_history'] = history
        # we add the initial prompt to the context
        context['init_prompt'] = self.init_prompt
        return context

    def show(self, *args, verbose:int=0, **kwargs):
        if verbose <=1:
            os.system('cls')
        self.data.show(*args, verbose=verbose, **kwargs)

