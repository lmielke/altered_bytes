"""
prompt_instructs.py

"""
import os, yaml
import altered.settings as sts
from colorama import Fore, Style
import altered.prompt_strategies as Strats
from altered.prompt_user_prompt import UserPrompt
from altered.yml_parser import YmlParser


class Instructions:
    default_strats = ['default_user_prompt', 'answer_simple']

    def __init__(self, name, *args, **kwargs):
        self.name = name

    def __call__(self, *args, **kwargs):
        s_names = self.get_strats_names(*args, **kwargs)
        strat_context = self.run_strats(s_names.get('strat'), *args, **kwargs)
        strat_io = self.run_io(s_names.get('io'), *args, **kwargs)
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
        if num_predict is not None:
            context['default_max_words'] = num_predict // 4
        return context

    def get_strats_names(self, *args, strat_templates:list=None, fmt:str=None, **kwargs):
        # we are calling the strat
        strat_templates = strat_templates or self.default_strats
        strat_templates = strat_templates if fmt is not None else strat_templates[:1]
        s_names = {}
        for s_name in strat_templates:
            method, _ = s_name.split('_', 1)
            if os.path.exists(os.path.join(sts.strats_dir, f'{s_name}.yml')):
                s_names['strat'] = {'method': method, 's_name': s_name}
            elif os.path.exists(os.path.join(sts.io_dir, f'{s_name}.yml')):
                s_names['io'] = {'method': method, 's_name': s_name}
        return s_names

    def run_strats(self, s_name:dict, *args, **kwargs):
        if s_name is None:
            return
        strat = getattr(Strats, s_name['method'].capitalize())(*args, **kwargs)\
                                                        (s_name['s_name'], *args, **kwargs)
        return strat

    def run_io(self, s_name:dict, *args, fmt:str='markdown', **kwargs):
        print(f"{Fore.YELLOW}{s_name = }{Fore.RESET}")
        if s_name is None:
            return
        template_path = os.path.join(sts.io_dir, f'{s_name["s_name"]}.yml')
        io = YmlParser(*args, fields_paths=[template_path], **kwargs).describe(fmt=fmt)
        return io.strip()

    def get_user_prompt(self, *args, **kwargs):
        user_prompt = UserPrompt(*args, **kwargs)(*args, **kwargs)
        return user_prompt

    def check_context(self, s_names:dict, user_prompt_context:dict, *args, **kwargs):
        print(f"{Fore.YELLOW}{s_names = }, {user_prompt_context = }{Fore.RESET}")
        if s_names.get('strat').get('method') == 'default' and \
                                            user_prompt_context.get('user_prompt') is None:
            msg = f"{Fore.RED}ERROR:{Fore.RESET} default strat requires a user_prompt"
            raise ValueError(msg)