"""
prompt.py

"""
import os, re, sys, yaml
from colorama import Fore, Style
from altered.model_connect import ModelConnect
import altered.settings as sts


class Prompt:

    prompts_file_name:str = 'prompt_basics.yml'
    prompt_params_path:str = os.path.join(sts.resources_dir, 'strategies', prompts_file_name)

    def __init__(self, *args, **kwargs):
        self.prompt_params = self.load_prompt_params(*args, **kwargs)
        self.assi = ModelConnect()

    def load_prompt_params(self, *args, **kwargs):
        with open(self.prompt_params_path, 'r') as f: 
            return yaml.safe_load(f)

    def mk_prompt(self, *args, **kwargs):
        context = self.prep_context(*args, **kwargs)
        user_prompt, instructs = self.prep_instructs(*args, **kwargs)
        # this is what the prompt will look like
        prompt = (
                    f"<context>\n"
                        f"{context}"
                    f"\n</context>\n"
                    
                    f"\n<user_prompt>\n"
                        f"{user_prompt.get('content', '# None')}"
                    f"\n</user_prompt>\n"
                    
                    f"\n<INST>\n"
                        f"{instructs}"
                    f"\n</INST>\n"
                    )
        return prompt

    def prep_instructs(self, user_prompt:dict=(), *args, instructs:str='', **kwags):
        msg = f"{Fore.RED} mk_prompt: Provide either user_prompt or instructs! {Fore.RESET}"
        assert user_prompt.get('content') or instructs, msg
        # depending on the inputs the prompt is constructed with user_prompt and instructs
        if user_prompt and not instructs:
            instructs = self.prompt_params.get('msg_and_not_instructs_prefix', '').strip()
        elif user_prompt and instructs:
            prefix = self.prompt_params.get('msg_and_instructs_prefix', '')
            instructs = re.sub( r'(<INST>\s+)(.*)(</INST>)', rf'\1{prefix}\2\3', instructs,
                                flags=re.MULTILINE,
                        ).strip()
        return user_prompt, instructs

    def prep_context(self, *args, context:str='', table, **kwargs):
        # we always add the chat chat_history for context (check if needed)
        if not table['content'].empty and (table['content'].str.len() > 0).any():
            context += "\n<chat_history>\n" + str(table['content']) + "\n</chat_history>\n"
        return context if context else 'None'

    def post(self, user_prompt:str, *args, depth:int=1, agg_method:str=None, **kwargs):
        # Post the message to the AI model
        # some params here are coming as kwargs from the source and are directly forwarded
        # Examples: alias='l3:8b_1', num_predict = 100,
        # This post method only retrieves text results
        kwargs['sub_domain'] = 'generates'
        kwargs['agg_method'] = 'best' if depth != 1 and (agg_method is None) else agg_method
        user_prompts = [user_prompt for _ in range(depth)]
        # we post the user prompt to the AI model
        r = self.assi.post(user_prompts, *args, **kwargs)
        return r