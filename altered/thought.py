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
        self.name, self.thought_dir = self.mk_thought_dir(name, *args, **kwargs)
        # user_promt that initiates the thought process/chain
        self.init_user_prompt = None
        # prompt constructor for LLM interaction
        self.prompt = Prompt(*args, **kwargs)
        # Data represents the thought table structure, where each line is a thought element
        self.data = Data(*args, name=name, data_dir=self.thought_dir, **kwargs)
        # lambda is needed for self.table because the obj reference breaks when rec is added
        self.table = lambda: getattr(self.data, self.name)

    def run(self, user_prompt:str=None, *args, **kwargs):
        # First we create the inital user_promt to run the chat
        if self.init_user_prompt is None: self.init_user_prompt = user_prompt
        self.user_prompt, self.response = user_prompt, None
        # the chat loop starts here
        # self.add_to_chat(user_prompt, *args, **kwargs)
        while not self.user_prompt in self.exit_terms:
            self.next_chat_item(*args, **kwargs)
        # exit uses /bye or /quit
        print(f"{Fore.GREEN}Finlizing Thought{Fore.RESET}")
        self.data.save_to_disk(*args, **kwargs)

    def mk_thought_dir(self, name:str, *args, **kwargs):
        name = re.sub(r'\W+', '_', name.lower())
        thought_dir = os.path.join(self.thoughts_dir, name)
        return name, thought_dir

    def next_chat_item(self, *args, **kwargs):
        # we send the user_prompt and the chat_history to the LLM (promt handles post())
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
        if isinstance(content, str): content = {'content': content, }
        content.update({'role': role, 'name': self.name})
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
