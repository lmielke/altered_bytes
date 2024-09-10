"""
chat.py
This class orchestrates the communication between the user and the AI assistant.
It stores and manages the chat chat_history and creates the chat message for the next prompt and
receives the response from the AI model. 
"""

import os, re, sys, yaml
from tabulate import tabulate as tb
from colorama import Fore, Style
from altered.data import Data
import altered.settings as sts
from altered.prompt import Prompt


class Chat:

    exit_terms = {'/bye', '/quit'}


    def __init__(self, name:str, *args, **kwargs):
        self.name = name
        self.init_prompt = None
        self.prompt = Prompt(*args, **kwargs)
        self.data = Data(*args, name=self.name, **kwargs)
        # lambda is needed here because the table reference breaks when data is added
        self.table = lambda: getattr(self.data, self.name)
        self.warnings = {}

    def run(self, user_prompt:str=None, *args, **kwargs):
        # First we create the inital user_promt to run the chat
        if self.init_prompt is None: self.init_prompt = user_prompt
        self.user_prompt, self.response = user_prompt, None
        # the chat loop starts here
        # self.add_to_chat(user_prompt, *args, **kwargs)
        while not self.user_prompt in self.exit_terms:
            self.next_chat_item(*args, **kwargs)
        # exit uses /bye or /quit
        print(f"{Fore.GREEN}Exiting Chat{Fore.RESET}")

    def next_chat_item(self, *args, **kwargs):
        # we send the user_prompt and the chat_history to the model (promt handles post())
        self.response = self.prompt(    *args,  
                                        user_prompt=self.user_prompt,
                                        context=self.prep_context(*args, **kwargs), 
                                        **kwargs, 
                        )
        # we add user_promt after getting the response to avoid having the current user_prompt
        # inside the chat_history
        self.add_to_chat(self.user_prompt, *args, role='user', **kwargs)
        self.add_to_chat(self.response, *args, role='assistant', **kwargs)
        lambda kwargs: os.system('cls') if not kwargs.get('verbose') else None
        self.data.show(*args, color=Fore.GREEN, **kwargs)
        self.user_prompt = self.get_user_prompt(*args, **kwargs)

    def get_user_prompt(self, *args, **kwargs) -> str:
        print(f"{Fore.YELLOW} \nWant to add a user_prompt to the next prompt ? {Fore.RESET}")
        user_prompt = input(f"You: ").strip()
        return user_prompt

    def add_to_chat(self, content:[str, dict], *args, role:str, **kwargs):
        if isinstance(content, str): content = {'content': content, 'role': role}
        self.data.append({k: content.get(k, None) for k, vs in self.data.fields.items()})

    def prep_context(self, *args, context:dict={}, **kwargs):
        context.update(self.prep_history(*args, **kwargs))
        return context

    def prep_history(self, *args, history:list=[], **kwargs):
        if not self.table()['content'].empty and (self.table()['content'].str.len() > 0).any():
            # we add the chat history for context (check if needed)
            for i, row in self.table().iterrows():
                if isinstance(row['content'], str):
                    history.append({'role':row['role'], 'content': row['content']})
        return {'chat_history': history if history else None}
