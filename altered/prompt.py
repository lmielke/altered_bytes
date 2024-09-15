"""
prompt.py

"""
import os
from colorama import Fore, Style
from altered.model_connect import ModelConnect
from altered.renderer import Render
from altered.prompt_context import Context
from altered.prompt_instructs import Instructions
import altered.hlp_printing as hlpp
import altered.settings as sts

default_aggreg = 'prompt_aggregations.best'


class Prompt:


    def __init__(self, *args, **kwargs):
        self.context = Context(*args, **kwargs)
        self.instructs = Instructions(*args, **kwargs)
        self.renderer = Render(*args, **kwargs)
        self.assi = ModelConnect()
        self.response = Response(*args, **kwargs)
        self.data = None
        self.warnings = {}

    def __call__(self, *args, **kwargs):
        self.context(*args, **kwargs)
        self.instructs(*args, **kwargs)
        return self.mk_prompt(*args, **kwargs)


    def mk_prompt(self, *args, context:dict={}, **kwargs):
        """
        Constructs the final prompt as to be send to the AI model.
        """
        self.context = { 
                            'prompt_title': 'LLM Prompt',
                            'context': self.context.data,
                            'user_prompt': self.instructs.user_prompt, 
                            'instruct': self.instructs.data,
        } 
        data = self.renderer.render(*args, 
                                                    template_name='prompt.md', 
                                                    context=self.context, 
                                                    **kwargs,
                    )
        hlpp.pretty_prompt(data, *args, **kwargs)
        return data


class Response:

    def __init__(self, *args, **kwargs):
        self.r = {}

    def __call__(self, *args, **kwargs):
        return self.extract(self.validate(*args, **kwargs), *args, **kwargs)

    def extract(self, r:dict, *args, depth:int=1, strategy:str=None, **kwargs) -> dict:
        strategy = default_aggreg if depth != 1 and strategy is None else strategy
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
            if result.get('strategy') == strategy:
                record.update(result)
                break
        else:
            # if we did not find the aggregation result, we take the last result in r
            # in case there was only a single result, the single result is the last result
            record = record.update(result)
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
