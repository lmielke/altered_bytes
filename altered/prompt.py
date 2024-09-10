"""
prompt.py

"""
import os
from colorama import Fore, Style
from altered.model_connect import ModelConnect
from altered.renderer import Render
from altered.prompt_context import Context
from altered.prompt_instructs import Instructions
import altered.hlp_printing as hlp_print
import altered.settings as sts


class Prompt:

    def __init__(self, *args, **kwargs):
        self.assi = ModelConnect()
        self.context = Context(*args, **kwargs)
        self.instructs = Instructions(*args, **kwargs)
        self.renderer = Render(*args, **kwargs)
        self._data = None

    def __call__(self, *args, **kwargs):
        self.mk_prompt(*args, **kwargs)
        return self.extract_response_content(self.post(*args, **kwargs), *args, **kwargs)

    def mk_prompt(self, *args, context:dict={}, **kwargs):
        """
        Constructs the final prompt as to be send to the AI model.
        """
        self._data = self.renderer.render(*args,
                    template_name='prompt.md', 
                    context={   
                                'prompt_title': 'LLM Prompt',
                                'context': self.context(*args, context=context, **kwargs).data,
                                'user_prompt': self.instructs(*args, **kwargs).user_prompt,
                                'instruct': self.instructs(*args, **kwargs).data,
                                },
                    **kwargs,
                        )
        # NOTE: to pretty print the prompt, provide a verbose flag >= 2
        hlp_print.pretty_prompt(self._data, *args, **kwargs)

    def post(self, *args,   alias:str = None, num_predict:int = None, depth:int=1,
                            agg_method:str=None, verbose:int = 0, **kwargs,
        ):
        # Construct model parameters specific to this Chat (see ModelConnect.get_params())
        model_params = {
                            'service_endpoint': 'get_generates',
                            'alias': alias,
                            'num_predict': num_predict,
                            'verbose': verbose,
                        }
        model_params['agg_method'] = 'best' if depth != 1 and (agg_method is None) \
                                                                            else agg_method
        # self._data is the prompt constructed by self.mk_prompt()
        # we post one or multiple user prompts to the AI model (depth == num of prompt reps)
        return self.assi.post([self._data for _ in range(depth)], *args, **model_params)

    def extract_response_content(self, r:dict, *args,   depth:int=1, 
                                                        agg_method:str=None, **kwargs
        ) -> dict:
        # r comes as a dictionary with 'results' containing a list of dictionaries
        agg_method = 'best' if depth != 1 and (agg_method is None) else agg_method
        results = r.get('results')
        if not results or type(results) != list:
            raise ValueError(f"Error: No results returned from the AI model.")
        for i, result in enumerate(results):
            if result.get('agg_method') == agg_method:
                response = result
                response['content'] = response.get('response').strip()
                response['role'] = 'assistant'
        return response
