"""
chat.py
This class orchestrates the communication between the user and the AI assistant.
It stores and manages the chat chat_history and creates the chat message for the next prompt and
receives the response from the AI LLM. 
"""

import os, re, sys, yaml
from tabulate import tabulate as tb
from colorama import Fore, Style

import altered.settings as sts
from altered.prompt import Prompt
from altered.data import Data


class Chat:

    exit_terms = {'/bye', '/quit'}
    chats_dir = os.path.join(sts.resources_dir, 'thoughts')


    def __init__(self, name:str, *args, **kwargs):
        # name of the chat can be used to locate/reference the saved chat
        print(f"{Fore.GREEN}Creating Chat {Fore.RESET}: {name = }")
        self.name, self.chat_dir = self.mk_chat_dir(name, *args, **kwargs)
        # initial user_promt provided by the user
        # prompt constructor for LLM interaction
        self.prompt = Prompt(*args, **kwargs)
        # Data represents the chat data structure, where each line is a chat element
        self._data = Data(*args, name=self.name, data_dir=self.chat_dir, **kwargs)

    @property
    def data(self, *args, **kwargs):
        return getattr(self._data, self.name)

    def run(self, *args, **kwargs):
        # First we create the inital user_promt to run the chat
        # the chat loop starts here
        # self.add_to_chat(running, *args, **kwargs)
        self.running = True
        while self.running:
            self.next_chat_item(*args, **kwargs)
        # exit uses /bye or /quit
        print(f"{Fore.GREEN}Finlizing Chat{Fore.RESET}")
        self._data.save_to_disk(*args, **kwargs)

    def mk_chat_dir(self, name:str, *args, **kwargs):
        name = re.sub(r'\W+', '_', name.lower())
        chat_dir = os.path.join(self.chats_dir, name)
        return name, chat_dir

    def next_chat_item(self, *args, **kwargs):
        # we call the prompt with whatever context we have
        print(f"{kwargs = }")
        self.p = self.prompt(*args, context=self.chat_history(*args, **kwargs), **kwargs)
        # we add user_promt after getting the response to avoid having the current running
        # inside the chat_history
        self.add_to_chat(self.p, *args, role='user', **kwargs)
        self.add_to_chat(self.p, *args, role='assistant', **kwargs)
        lambda kwargs: os.system('cls') if not kwargs.get('verbose') else None
        self._data.show(*args, color=Fore.GREEN, **kwargs)
        self.running = self.p.get('running')

    def add_to_chat(self, record:[str, dict], *args, role:str, **kwargs):
        new_record = {k: record.get(k, None) for k, vs in self._data.fields.items()}
        if role == 'user':
            new_record['content'] = record.get('user_prompt')
            new_record['prompt'] = 'next line'
        new_record.update({'role': role, 'name': self.name})
        self._data.append(new_record)

    def chat_history(self, *args, history:list=[], **kwargs) -> list[dict]:
        if not self.data['content'].empty and (self.data['content'].str.len() > 0).any():
            # we add the chat history for context (check if needed)
            for i, row in self.data.iterrows():
                if isinstance(row['content'], str):
                    history.append({'role':row['role'], 'content': row['content']})
        return {'chat_history': history if history else None}
