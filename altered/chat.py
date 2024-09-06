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
        self.init_msg = None
        self.prompt = Prompt()
        self.data = Data(name=self.name)
        # lambda is needed here because the table reference breaks when data is added
        self.table = lambda: getattr(self.data, self.name)

    def run(self, user_input:str=None, *args, **kwargs):
        # First we create the inital user_promt to run the chat
        user_prompt = {'content': user_input, 'role': 'user'}
        if self.init_msg is None: self.init_msg = user_prompt
        # the chat loop starts here
        # self.add_to_chat(user_prompt, *args, **kwargs)
        while not user_prompt['content'] in self.exit_terms:
            context = self.prep_context(*args, **kwargs)
            self.add_to_chat(user_prompt, *args, **kwargs)
            r = self.prompt(user_prompt, *args, context=context, **kwargs)
            response = self.extract_response_content(r, *args, **kwargs)
            os.system('cls')
            self.add_to_chat(response, *args, **kwargs)
            self.data.show(*args, color=Fore.GREEN, **kwargs)
            user_prompt = self.get_user_input(*args, **kwargs)
        print(f"{Fore.GREEN}Exiting Chat{Fore.RESET}")

    def get_user_input(self, *args, **kwargs) -> str:
        print(f"{Fore.YELLOW} \nWant to add a user_prompt to the next prompt ? {Fore.RESET}")
        user_input = input(f"You: ").strip()
        user_prompt = {'content': user_input, 'role': 'user'}
        return user_prompt

    def extract_response_content(self, r:dict, *args,   depth:int=1, 
                                                        agg_method:str=None, **kwargs
        ) -> dict:
        # r comes as a dictionary with 'results' containing a list of dictionaries
        agg_method = 'best' if depth != 1 and (agg_method is None) else agg_method
        results = r.get('results')
        if not results or type(results) != list:
            raise ValueError(f"Error: No results returned from the AI model.")
        for i, result in enumerate(results):
            if result.get('agg_method') == agg_method:
                response = result
                response['content'] = response.get('response').strip()
                response['role'] = 'assistant'
        return response

    def add_to_chat(self, prompt:str, *args, **kwargs):
        rec = self.mk_record(prompt, *args, **kwargs)
        self.data.append(rec)

    def mk_record(self, result:str, *args, **kwargs):
        rec = {k: result.get(k, None) for k, vs in self.data.fields.items()}
        return rec

    def prep_context(self, *args, context: str = '', **kwargs):
        if not self.table()['content'].empty and (self.table()['content'].str.len() > 0).any():
            # we add the chat history for context (check if needed)
            history = '\n'.join(
                                    [
                                        f"{i}: {row['role']} -> {row['content']}"
                                            for i, row in self.table().iterrows()
                                                if isinstance(row['content'], str)
                                    ]
            )

            context += (
                            f"\n<chat_history>\n"
                                f"{history}"
                            f"\n</chat_history>\n"
            )

        return context if context else 'None'
