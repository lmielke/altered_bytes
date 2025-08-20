"""
prompt_instructs.py

"""
import os, yaml
import altered.settings as sts
from colorama import Fore, Style
import altered.prompt_strategies as Strats
import altered.prompt_io as Io
from altered.yml_parser import YmlParser


class Instructions:
    default_strats = 'default_user_prompt'
    default_io = None
    max_words, letters_per_word = 500, 4
    template_name = 'i_instructs.md'

    def __init__(self, name, *args, fmt:str=None, **kwargs):
        self.name = name
        self.fmt = fmt
        self.inputs = None
        self.context = {}
        self.params = {}

    def __call__(self, *args, **kwargs):
        self.get_instruct_params(*args, **kwargs)
        strat_context, self.fmt = self.run_strats(*args, **kwargs)
        strat_io = self.run_io(*args, **kwargs)
        self.mk_context(strat_context, strat_io, *args, **kwargs)
        return self

    def mk_context(self, strat_context, strat_io, *args, **kwargs, ):
        self.context = {
                    'strats': strat_context, 
                    'io': strat_io,
                    'fmt': self.fmt,
                }
        # if time revise how num_predict is derrived (check kwargs['num_predict'])
        self.context['num_predict'] = max(  
            strat_context.get('validations', {}).get('expected_words', (0, 0))[-1],
            strat_context['num_predict'] if strat_context['num_predict'] is not None else 0,
            self.max_words, 
            )
        return self.context

    def get_instruct_params(self, *args, strat_template:str=None, **kwargs):
        # we are calling the strat
        strat_template = strat_template or self.default_strats
        strats = [n.split('.')[0] for n in os.listdir(sts.strats_dir) if '_' in n]
        if strat_template not in strats:
            raise ValueError(f"{Fore.RED}{strat_template} not in {strats}{Fore.RESET}")
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
        if io_template is None or not os.path.isfile(
                                                os.path.join(sts.io_dir, f"{io_template}.yml")
                                        ):
            return None
        io = getattr(Io, io_template.split('_', 1)[0].capitalize())(*args, **kwargs,
            )(io_template, *args, fmt=self.fmt, **kwargs)
        return io
