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
import altered.hlp_printing as hlp_print
from altered.model_connect import ModelConnect


class Chat:

    prompts_file_name:str = 'prompt_basics.yml'
    prompt_params_path:str = os.path.join(sts.resources_dir, 'strategies', prompts_file_name)
    exit_terms = {'/bye', '/quit'}

    def __init__(self, name:str, *args, **kwargs):
        self.name = name
        self.prompt_params = self.load_prompt_params(*args, **kwargs)
        self.init_msg = None
        self.data = Data(name=self.name)
        self.table = getattr(self.data, self.name)
        self.assi = ModelConnect()

    def load_prompt_params(self, *args, **kwargs):
        with open(self.prompt_params_path, 'r') as f: 
            return yaml.safe_load(f)

    def run(self, user_input:str=None, *args, **kwargs):
        # First we create the inital user_promt to run the chat
        user_prompt = {'content': user_input, 'role': 'user'}
        if self.init_msg is None: self.init_msg = user_prompt
        # the chat loop starts here
        while not user_prompt['content'] in self.exit_terms:
            prompt = self.mk_prompt(user_prompt, *args, **kwargs)
            hlp_print.pretty_prompt(prompt, *args, **kwargs)
            response = self.post(prompt, *args, **kwargs)
            os.system('cls')
            self.add_to_chat(response, *args, **kwargs)
            self.data.show(*args, color=Fore.GREEN, **kwargs)
            user_prompt = self.get_user_input(*args, **kwargs)
            self.add_to_chat(user_prompt, *args, **kwargs)
        print(f"{Fore.GREEN}Exiting Chat{Fore.RESET}")

    def get_user_input(self, *args, **kwargs) -> str:
        print(f"{Fore.YELLOW} \nWant to add a user_prompt to the next prompt ? {Fore.RESET}")
        user_input = input(f"You: ").strip()
        user_prompt = {'content': user_input, 'role': 'user'}
        return user_prompt

    def mk_prompt(self, user_prompt:str='', *args, instructs:str='', context:str='', **kwargs):
        msg = f"{Fore.RED} mk_prompt: Provide either user_prompt or instructs! {Fore.RESET}"
        assert user_prompt.get('content') or instructs, msg
        # we always add the chat chat_history for context (check if needed)
        table = getattr(self.data, self.name)
        if not table['content'].empty and (table['content'].str.len() > 0).any():
            context += "\n<chat_history>\n" + str(table['content']) + "\n</chat_history>\n"
        # depending on the inputs the prompt is constructed with user_prompt and instructs
        if user_prompt and not instructs:
            instructs = self.prompt_params.get('msg_and_not_instructs_prefix', '')
        elif instructs and not user_prompt:
            pass
        if user_prompt and instructs:
            prefix = self.prompt_params.get('msg_and_instructs_prefix', '')
            instructs = re.sub( r'(<INST>\s+)(.*)(</INST>)', rf'\1{prefix}\2\3', instructs,
                                flags=re.MULTILINE,
                        )

        context = f"<context>\n{context if context else 'None'}\n</context>"
        user_prompt = f"<user_prompt>\n{user_prompt['content']}\n</user_prompt>" if user_prompt else ''
        instructs = f"<INST>\n{instructs}\n</INST>" if instructs else ''
        return (f"{context}\n{user_prompt}\n\n{instructs}").strip().strip('\n')

    def post(self, user_prompt:str, *args, depth:int=1, agg_method:str=None, **kwargs):
        # Post the message to the AI model
        user_prompts = [user_prompt for _ in range(depth)]
        r = self.assi.post(
                                            user_prompts,
                                            alias='l3:8b_1',
                                            num_predict = 100,
                                            sub_domain='generates',
                                            agg_method=agg_method,
                        )
        print(f"\nr: {r}")
        

        exit()



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