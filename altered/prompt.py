"""
prompt.py

"""
import os, re, sys, yaml
from colorama import Fore, Style
from altered.model_connect import ModelConnect
import altered.hlp_printing as hlp_print
import altered.settings as sts


class Prompt:

    prompts_file_name:str = 'prompt_basics.yml'
    prompt_params_path:str = os.path.join(sts.resources_dir, 'strategies', prompts_file_name)

    def __init__(self, *args, **kwargs):
        self.prompt_params = self.load_prompt_params(*args, **kwargs)
        self.assi = ModelConnect()

    def __call__(self, *args, **kwargs):
        prompt = self.mk_prompt(*args, **kwargs)
        return self.post(prompt, *args, **kwargs)

    def load_prompt_params(self, *args, **kwargs):
        with open(self.prompt_params_path, 'r') as f: 
            return yaml.safe_load(f)

    def mk_prompt(self, *args, context:str, **kwargs):
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
        hlp_print.pretty_prompt(prompt, *args, **kwargs)
        return prompt

    def prep_instructs(self, user_prompt:dict=(), *args, instructs:str='', **kwags):
        msg = f"{Fore.RED} mk_prompt: Provide either user_prompt or instructs! {Fore.RESET}"
        assert user_prompt.get('content') or instructs, msg
        # depending on the inputs the prompt is constructed with user_prompt and instructs
        if user_prompt and not instructs:
            # this should instruct the model to respond to the user_prompt directly
            instructs = self.prompt_params.get('msg_and_not_instructs_prefix', '')
        elif user_prompt and instructs:
            # in this case the user_prompt is only additional context to the prompt
            # the model should respond to the instructs and not the user_prompt
            prefix = self.prompt_params.get('msg_and_instructs_prefix', '')
            instructs = f"{prefix}\n\n{instructs}"
        return user_prompt, instructs

    def post(self, user_prompt:str, *args, depth:int=1, agg_method:str=None, **kwargs):
        # Post the message to the AI model
        # some params here are coming as kwargs from the source and are directly forwarded
        # Examples: alias='l3:8b_1', num_predict = 100,
        # This post method only retrieves text results
        if kwargs.get('context'): del kwargs['context']
        kwargs['sub_domain'] = 'generates'
        kwargs['agg_method'] = 'best' if depth != 1 and (agg_method is None) else agg_method
        user_prompts = [user_prompt for _ in range(depth)]
        # we post the user prompt to the AI model
        return self.assi.post(user_prompts, *args, **kwargs)
