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


class Prompt:
    default_aggreg = 'prompt_aggregations.best'

    def __init__(self, *args, **kwargs):
        self.assi = ModelConnect()
        self.context = Context(*args, **kwargs)
        self.instructs = Instructions(*args, **kwargs)
        self.renderer = Render(*args, **kwargs)
        self._data = None
        self.warnings = {}

    def __call__(self, *args, **kwargs):
        self.context(*args, **kwargs)
        self.instructs(*args, **kwargs)
        self.mk_prompt(*args, **kwargs)
        self.post(self.update_model_params(*args, **kwargs), *args, **kwargs)
        return self.extract(*args, **kwargs)

    def mk_prompt(self, *args, context:dict={}, **kwargs):
        """
        Constructs the final prompt as to be send to the AI model.
        """
        self.context = { 'prompt_title': 'LLM Prompt',
                        'context': self.context.data,
                        'user_prompt': self.instructs.user_prompt, 
                        'instruct': self.instructs.data,
        } 
        self._data = self.renderer.render(*args, 
                                                    template_name='prompt.md', 
                                                    context=self.context, 
                                                    **kwargs,
                    )
        # NOTE: to pretty print the prompt, provide a verbose flag >= 2
        hlpp.pretty_prompt(self._data, *args, **kwargs)

    def update_model_params(self, *args, alias:str=None, num_predict:int=None, depth:int=1,
                            strategy:str=None, verbose:int=0, **kwargs,
        ):
        # Construct model parameters specific to this Chat (see ModelConnect.get_params())
        server_params = {
                    'service_endpoint': 'get_generates',
                    'alias': alias,
                    'num_predict': num_predict,
                    'verbose': verbose,
                    'strategy': self.default_aggreg if depth != 1 and strategy is None else strategy
                        }
        server_params.update({k:vs for k, vs in kwargs.items() if not k in {'context',}})
        return server_params
        
    def post(self, server_params:dict, *args, depth:int=1, **kwargs):
        # self._data is the prompt constructed by self.mk_prompt()
        # we post one or multiple user prompts to the AI model (depth == num of prompt reps)
        self.r = Prompt.validate(
                                    self.assi.post(
                                                    [self._data for _ in range(depth)], 
                                                    *args, **server_params,
                                    ), *args, **kwargs,
                )

    def extract(self, *args, depth:int=1, strategy:str=None, **kwargs) -> dict:
        # r comes as a dictionary with 'results' containing a list of dictionaries
        if not self.r.get('responses') or type(self.r.get('responses')) != list:
            raise ValueError(f"Error: No valid responses returned from the AI model.")
        strategy = self.default_aggreg if depth != 1 and (strategy is None) else strategy
        # we create the output record 
        record = {
                        'user_prompt': self.context['user_prompt'], 
                        'prompt': self._data,
                        'role': 'assistant',
                        'model': self.r.get('model'),
                    }
        # r might have a single result or mulitple responses. We only return a single result.
        for i, result in enumerate(self.r.get('responses')):
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
        elif '</INST>' in resp_content:
            # content most likely contains the instruction tag which we remove here
            resp_content = resp_content.split('</INST>')
            if len(resp_content) > 2:
                raise ValueError(f"Error: Multiple Instruction Tags Found")
            elif len(resp_content) == 2:
                resp_content = resp_content[-1].strip()
        r['responses'][0]['response'] = resp_content
        return r
