"""
prompt_instructs.py

"""
import os, yaml
import altered.settings as sts
from colorama import Fore, Style
import altered.prompt_strategies as Strats
import altered.prompt_io as Io
from altered.prompt_user_prompt import UserPrompt
from altered.yml_parser import YmlParser


class Instructions:
    default_strats = ['default_user_prompt', 'simple_answer']
    max_words = 250
    template_name = 'i_instructs.md'

    def __init__(self, name, *args, **kwargs):
        self.name = name

    def __call__(self, *args, **kwargs):
        s_names = self.get_strats_names(*args, **kwargs)
        strat_context = self.run_strats(s_names.get('strat'), *args, **kwargs)
        strat_io = self.run_io(*args, **kwargs)
        user_prompt_context = self.get_user_prompt(*args, **kwargs)
        self.check_context(s_names, user_prompt_context, *args, **kwargs)
        return self.mk_context(strat_context, user_prompt_context, strat_io, *args, **kwargs)

    def mk_context(self, strat_context, user_prompt_context, strat_io, *args,
                            num_predict:int=None,
                            **kwargs,
        ):
        context = {
                    'strats': strat_context, 
                    'user_prompt': user_prompt_context, 
                    'io': strat_io,
                }
        context['response_max_words'] = self.max_words if num_predict is None else \
                                                                        num_predict // 4
        return context

    def get_strats_names(self, *args, strat_templates:list=None, **kwargs):
        # we are calling the strat
        strat_templates = strat_templates or self.default_strats
        # strat_templates = strat_templates if fmt is not None else strat_templates[:1]
        s_names = {}
        for s_name in strat_templates:
            method, _ = s_name.split('_', 1)
            if os.path.exists(os.path.join(sts.strats_dir, f'{s_name}.yml')):
                s_names['strat'] = {'method': method, 's_name': s_name}
        return s_names

    def run_strats(self, s_name:dict, *args, **kwargs):
        if s_name is None:
            return
        strat = getattr(Strats, s_name['method'].capitalize())(*args, **kwargs)\
                                                        (s_name['s_name'], *args, **kwargs)
        return strat

    def run_io(self, *args, io_template:str=None, **kwargs):
        if io_template is None:
            return
        io = getattr(Io, io_template.split('_', 1)[0].capitalize())(*args, **kwargs)\
                                                        (io_template, *args, **kwargs)
        return io

    def get_user_prompt(self, *args, **kwargs):
        user_prompt = UserPrompt(*args, **kwargs)(*args, **kwargs)
        return user_prompt

    def check_context(self, s_names:dict, user_prompt_context:dict, *args, **kwargs):
        if s_names.get('strat').get('method') == 'default' and \
                                            user_prompt_context.get('user_prompt') is None:
            msg = f"{Fore.RED}ERROR:{Fore.RESET} default strat requires a user_prompt"
            raise ValueError(msg)