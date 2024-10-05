"""
prompt.py

"""
import os
from colorama import Fore, Style
from altered.renderer import Render
from altered.prompt_context import Context
from altered.prompt_instructs import Instructions
from altered.model_connect import SingleModelConnect
import altered.hlp_printing as hlpp
import altered.settings as sts

default_aggreg = 'default_user_prompt'


class Prompt:


    def __init__(self, name, *args, **kwargs):
        self.name = name
        print(f"{Fore.BLUE}{Style.BRIGHT}Prompt.__init__.in {kwargs = }{Style.RESET_ALL}")
        self.C = Context(name, *args, **kwargs)
        self.I = Instructions(name, *args, **kwargs)
        self.RD = Render(*args, **kwargs)
        self.data = None
        self.warnings = {}
        print(f"{Fore.BLUE}{Style.BRIGHT}Prompt.__init__.out {kwargs = }{Style.RESET_ALL}")

    def __call__(self, *args, **kwargs):
        self.mk_prompt(*args, **kwargs)
        self.render_prompt(*args, **kwargs)
        return self


    def mk_prompt(self, *args, **kwargs):
        """
        Constructs the final prompt as to be send to the AI model.
        """
        self.context = { 
                            'prompt_title': f"Prompt for {self.name}",
                            'context': self.get_context(*args, **kwargs),
                            'instructs': self.get_instructs(*args, **kwargs),
                        }

    def render_prompt(self, *args, context:dict=None, **kwargs):
        self.data = self.RD.render(*args, 
                                                    template_name='prompt.md', 
                                                    context=self.context, 
                                                    **kwargs,
                    )
        hlpp.pretty_prompt(self.data, *args, **kwargs)

    def get_context(self, *args, **kwargs):
        context_dict = self.C(*args, **kwargs)
        return context_dict

    def get_instructs(self, *args, **kwargs):
        instructs = self.I(*args, **kwargs)
        return instructs


class Response:

    def __init__(self, *args, **kwargs):
        self.r = {}

    def __call__(self, *args, **kwargs):
        return self.extract(self.validate(*args, **kwargs), *args, **kwargs)

    def extract(self, r:dict, *args, repeats:int=1, strat_templates:str=None, **kwargs) -> dict:
        strat_templates = [default_aggreg] if repeats != 1 and strat_templates is None else strat_templates
        # r comes as a dictionary with 'results' containing a list of dictionaries
        if not r.get('responses') or type(r.get('responses')) != list:
            raise ValueError(f"Error: No valid responses returned from the AI model.")
        # we create the output record 
        record = {
                        'user_prompt': r.get('user_prompt'),
                        'role': 'assistant',
                        'model': r.get('model'),
                    }
        # r might have a single result or mulitple responses. We only return a single result.
        for i, result in enumerate(r.get('responses')):
            if result.get('strat_template') is not None:
                if strat_templates[0] == result.get('strat_template'):
                    record.update(result)
                    break
        else:
            # if we did not find the aggregation result, we take the last result in r
            # in case there was only a single result, the single result is the last result
            record.update(result)
        record['content'] = record.get('response').strip()
        return record


    @staticmethod
    def validate(r:dict, *args, **kwargs) -> dict:
        resp_content = r.get('responses')[0].get('response').strip()
        if not resp_content:
            raise ValueError(f"Error: No response content returned from the AI model.")
        if '</INST>' in resp_content:
            # content most likely contains the instruction tag which we remove here
            resp_content = resp_content.split('</INST>')
            if len(resp_content) > 2:
                raise ValueError(f"Error: Multiple Instruction Tags Found")
            elif len(resp_content) == 2:
                resp_content = resp_content[-1].strip()
        r['responses'][0]['response'] = resp_content
        return r
