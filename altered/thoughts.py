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

import altered.settings as sts
from altered.model_connect import ModelConnect
from altered.prompt import Prompt, Response
from altered.data import Data


class Chat:

    exit_terms = {'/bye', '/quit'}
    roles = ('user', 'assistant')
    chats_dir = os.path.join(sts.resources_dir, 'thoughts')


    def __init__(self, name:str, *args, **kwargs):
        # name of the chat can be used to locate/reference the saved chat
        self.name, self.chat_dir = self.get_chat_dir(name, *args, **kwargs)
        self.assi = ModelConnect(*args, **kwargs)
        # initial user_promt provided by the user
        # prompt constructor for LLM interaction
        self.prompt = Prompt(*args, **kwargs)
        self.response = Response(*args, **kwargs)
        # Data represents the chat data structure, where each line is a chat element
        self.data = Data(*args, name=self.name, data_dir=self.chat_dir, **kwargs)

    def run(self, *args, **kwargs):
        # First we create the inital user_promt to run the chat
        # the chat loop starts here
        # self.mk_data_record(running, *args, **kwargs)
        self.running = True
        while self.running:
            self.running = self.next_chat_item(*args, **kwargs)
        # exit uses /bye or /quit
        self.data.save_to_disk(*args, **kwargs)

    def get_chat_dir(self, name:str, *args, **kwargs):
        name = re.sub(r'\W+', '_', name.lower())
        chat_dir = os.path.join(self.chats_dir, name)
        return name, chat_dir

    def next_chat_item(self, *args, **kwargs):
        # we call the prompt with history since all other context is handled by prompt
        self.p = self.prompt(*args, context=self.data.mk_history(*args, **kwargs), **kwargs)
        # response handles post model cleanup
        self.r = self.response(self.post(*args, **kwargs), *args, **kwargs)
        # we create the next record to update the chat
        for role in self.roles:
            self.data.append(self.mk_data_record(*args, role=role, **kwargs))
        self.show(*args, **kwargs)
  
    def post(self, *args, depth:int=1, **kwargs):
        server_params = self.update_model_params(*args, **kwargs)
        # we post one or multiple user prompts to the AI model (depth == num of prompt reps)
        return self.assi.post([self.p for _ in range(depth)], *args, **server_params, )

    def mk_data_record(self, *args, role:str, user_prompt:str, **kwargs):
        record = {k: self.r.get(k, None) for k, vs in self.data.fields.items()}
        record.update({'role': role, 'name': self.name})
        # for role 'user' the prompt is displayed together with the answer/response
        if role == 'user':
            record['content'] = user_prompt
            record['prompt'] = 'next line'
        elif role == 'assistant':
            record['prompt'] = self.p
        return record

    def update_model_params(self, *args, alias:str=None, num_predict:int=None, depth:int=1,
                            strategy:str=None, verbose:int=0, **kwargs,
        ):
        # Construct model parameters specific to this Chat (see ModelConnect.get_params())
        strategy = default_aggreg if depth != 1 and strategy is None else strategy
        server_params = {
                            'service_endpoint': 'get_generates',
                            'alias': alias,
                            'num_predict': num_predict,
                            'verbose': verbose,
                            'strategy': strategy
                        }
        server_params.update({k:vs for k, vs in kwargs.items() if not k in {'context',}})
        return server_params

    def show(self, *args, verbose:int=0, **kwargs):
        if verbose <=1:
            os.system('cls')
        self.data.show(*args, verbose=verbose, **kwargs)

