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


class Thought:

    exit_terms = {'/bye', '/quit'}
    thoughts_dir = os.path.join(sts.resources_dir, 'thoughts')


    def __init__(self, name:str, *args, **kwargs):
        # name of the thought can be used to locate/reference the saved thought
        print(f"{Fore.GREEN}Creating Thought {Fore.RESET}: {name = }")
        self.name, self.thought_dir = self.mk_thought_dir(name, *args, **kwargs)
        # initial user_promt provided by the user
        # prompt constructor for LLM interaction
        self.prompt = Prompt(*args, **kwargs)
        # Data represents the thought table structure, where each line is a thought element
        self.data = Data(*args, name=self.name, data_dir=self.thought_dir, **kwargs)

    @property
    def table(self, *args, **kwargs):
        return getattr(self.data, self.name)

    def run(self, *args, **kwargs):
        # First we create the inital user_promt to run the chat
        # the chat loop starts here
        # self.add_to_chat(still_thinking, *args, **kwargs)
        self.still_thinking = True
        while self.still_thinking:
            self.next_chat_item(*args, **kwargs)
        # exit uses /bye or /quit
        print(f"{Fore.GREEN}Finlizing Thought{Fore.RESET}")
        self.data.save_to_disk(*args, **kwargs)

    def mk_thought_dir(self, name:str, *args, **kwargs):
        name = re.sub(r'\W+', '_', name.lower())
        thought_dir = os.path.join(self.thoughts_dir, name)
        return name, thought_dir

    def next_chat_item(self, *args, **kwargs):
        # we call the prompt with whatever context we have
        print(f"{kwargs = }")
        self.p = self.prompt(*args, context=self.thought_history(*args, **kwargs), **kwargs)
        # we add user_promt after getting the response to avoid having the current still_thinking
        # inside the chat_history
        # self.add_to_chat(self.p.get('still_thinking'), *args, role='user', **kwargs)
        self.add_to_chat(self.p, *args, role='user', **kwargs)
        self.add_to_chat(self.p, *args, role='assistant', **kwargs)
        lambda kwargs: os.system('cls') if not kwargs.get('verbose') else None
        self.data.show(*args, color=Fore.GREEN, **kwargs)
        self.still_thinking = self.p.get('still_thinking')

    def add_to_chat(self, record:[str, dict], *args, role:str, **kwargs):
        new_record = {k: record.get(k, None) for k, vs in self.data.fields.items()}
        if role == 'user':
            new_record['content'] = record.get('user_prompt')
            new_record['prompt'] = 'next line'
        new_record.update({'role': role, 'name': self.name})
        self.data.append(new_record)

    def thought_history(self, *args, history:list=[], **kwargs) -> list[dict]:
        if not self.table['content'].empty and (self.table['content'].str.len() > 0).any():
            # we add the chat history for context (check if needed)
            for i, row in self.table.iterrows():
                if isinstance(row['content'], str):
                    history.append({'role':row['role'], 'content': row['content']})
        return {'chat_history': history if history else None}
