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
    default_strats = 'default_user_prompt'
    default_io = None
    max_words = 250
    template_name = 'i_instructs.md'

    def __init__(self, name, *args, fmt:str=None, **kwargs):
        self.name = name
        self.fmt = fmt
        self.context = {}
        self.params = {}

    def __call__(self, *args, **kwargs):
        self.get_instruct_params(*args, **kwargs)
        strat_context, self.fmt = self.run_strats(*args, **kwargs)
        strat_io = self.run_io(*args, **kwargs)
        user_prompt_context = self.get_user_prompt(*args, **kwargs)
        self.check_context(user_prompt_context, *args, **kwargs)
        self.mk_context(strat_context, user_prompt_context, strat_io, *args, **kwargs)
        return self

    def mk_context(self, strat_context, user_prompt_context, strat_io, *args,
                            num_predict:int=None,
                            **kwargs,
        ):
        self.context = {
                    'strats': strat_context, 
                    'user_prompt': user_prompt_context, 
                    'io': strat_io,
                }
        self.context['response_max_words'] = self.max_words if num_predict is None else \
                                                                        num_predict // 4
        return self.context

    def get_instruct_params(self, *args, strat_template:str=None, **kwargs):
        # we are calling the strat
        strat_template = strat_template or self.default_strats
        method, sub_method = strat_template.split('_', 1)
        if os.path.exists(os.path.join(sts.strats_dir, f'{strat_template}.yml')):
            self.params = {'method': method, 't_name': strat_template, 'sub_method': sub_method}
        return self.params

    def run_strats(self, *args, **kwargs):
        if not self.params:
            return None
        return getattr(Strats, self.params['method'].capitalize())(*args, **kwargs,
                )(*args, params=self.params, **kwargs)

    def run_io(self, *args, io_template:str=None, fmt:str=None, **kwargs):
        if io_template is None or not os.path.isfile(os.path.join(sts.io_dir, io_template)):
            return None
        io = getattr(Io, io_template.split('_', 1)[0].capitalize())(*args, **kwargs,
            )(io_template, *args, fmt=self.fmt, **kwargs)
        return io

    def get_user_prompt(self, *args, **kwargs):
        user_prompt = UserPrompt(*args, **kwargs)(*args, **kwargs)
        return user_prompt

    def check_context(self, user_prompt_context:dict, *args, **kwargs):
        if self.params.get('method') == 'default' and \
                                            user_prompt_context.get('user_prompt') is None:
            msg = f"{Fore.RED}ERROR:{Fore.RESET} default strat requires a user_prompt"
            raise ValueError(msg)