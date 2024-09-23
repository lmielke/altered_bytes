"""
prompt.py

"""
import os
from colorama import Fore, Style
from altered.renderer import Render
from altered.prompt_context import Context
from altered.prompt_instructs import Instructions
from altered.model_connect import ModelConnect
import altered.hlp_printing as hlpp
import altered.settings as sts

default_aggreg = 'agg_mean'


class Prompt:


    def __init__(self, *args, **kwargs):
        self.context = Context(*args, **kwargs)
        self.instructs = Instructions(*args, **kwargs)
        self.renderer = Render(*args, **kwargs)
        self.response = Response(*args, **kwargs)
        self.assi = ModelConnect(*args, **kwargs)
        self.data = None
        self.warnings = {}

    def __call__(self, *args, **kwargs):
        print(f"Prompt.__call__: {kwargs = }")
        self.mk_prompt(*args, **kwargs)
        return self.render_prompt(*args, **kwargs)


    def mk_prompt(self, *args, **kwargs):
        """
        Constructs the final prompt as to be send to the AI model.
        """
        self.context_dict = { 
                            'prompt_title': 'LLM Prompt',
                            'context': self.get_context(*args, **kwargs),
                            'instructs': self.get_instructs(*args, **kwargs),
                        }

    def render_prompt(self, *args, context:dict=None, **kwargs):
        print(f"Prompt.render_prompt: {context = }")
        print(f"Prompt.render_prompt: {self.context_dict = }")
        data = self.renderer.render(*args, 
                                                    template_name='prompt.md', 
                                                    context=self.context_dict, 
                                                    **kwargs,
                    )
        hlpp.pretty_prompt(data, *args, **kwargs)
        return data

    def get_context(self, *args, **kwargs):
        context_dict = self.context(*args, **kwargs)
        return context_dict

    def get_instructs(self, *args, **kwargs):
        instructs = self.instructs(*args, **kwargs)
        return instructs




class Response:

    def __init__(self, *args, **kwargs):
        self.r = {}

    def __call__(self, *args, **kwargs):
        return self.extract(self.validate(*args, **kwargs), *args, **kwargs)

    def extract(self, r:dict, *args, repeats:int=1, strat_templates:str=None, **kwargs) -> dict:
        strat_templates = [default_aggreg] if repeats != 1 and strat_templates is None else strat_templates
        print(f"{Fore.RED}Response.extract:{Fore.RESET} {strat_templates = }")
        # r comes as a dictionary with 'results' containing a list of dictionaries
        if not r.get('responses') or type(r.get('responses')) != list:
            raise ValueError(f"Error: No valid responses returned from the AI model.")
        # we create the output record 
        record = {
                        'user_prompt': r.get('user_prompt'),
                        'prompt': r.get('prompt'),
                        'role': 'assistant',
                        'model': r.get('model'),
                    }
        # r might have a single result or mulitple responses. We only return a single result.
        for i, result in enumerate(r.get('responses')):
            print(f"{Fore.RED}extract {i}{Fore.RESET}: {result.get('response') = }")
            print(f"{Fore.RED}template {i}{Fore.RESET}: {result.get('strat_templates') = }")
            if result.get('strat_templates') is not None:
                if strat_templates[0] == result.get('strat_templates')[0]:
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
