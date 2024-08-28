# assistant.py

import altered.model_params as msts
from typing import Dict, Union, Tuple
from openai import OpenAI
import json
import re
import requests
from colorama import Fore, Style
import random as rd

class ModelConnect:
    """
    ModelConnect handles the communication with an AI assistant of your choice.
    For some assistants, Ollama is currently hosting and running the models. 
    See model_settings.models for the assistants and their respective models.
    The remote Ollama machines are listening on 0.0.0.0:11434 and are accessible 
    via the local private Network. 
    """
    
    def __init__(self, *args, **kwargs) -> None:
        self.min_context_len = 2000
        self.to_msgs = lambda m: [{'role': 'user', 'content': m}]


    def random_temp(self, lower:float=None, upper:float=None) -> float:
        if lower is None:
            lower = 0.1
        if upper is None:
            upper = 0.8
        rd_temp = min(max(lower, rd.random()), upper)
        print(f"{Fore.YELLOW}Warning {Fore.RESET}random temperature set: {rd_temp:.2f}")

    def get_params(self, message:[str, list], *args, sub_domain:str,
                                                        name:str,
                                                        context_length:int,
                                                        stream:str=False,
                                                        temperature:float=None,
                                                        num_predict:int=None,
                                                        aggregation_method:str=None,
                                                        **kwargs,
        ) -> dict:
        print(f"{Fore.YELLOW}sub_domain: {sub_domain}{Fore.RESET}")
        if sub_domain in ['get_embeddings', 'generates']:
            # for embeddings and generate[s]! message is a list, to allow for multiple messages to be embedded
            # with a single server call
            msg = ( 
                    f"{Fore.YELLOW}WARNING{Fore.RESET}: "
                    f"Expected message to be a list, "
                    f"but got {Fore.YELLOW}{type(message)}{Fore.RESET} instead.\n"
                    f"Converting to List"
                    )
            if type(message) != list:
                print(message)
                message = [str(message)]
            # for embeddings we want the temperature to be low to be more deterministic
            temperature = temperature if temperature is not None else 0.
        temperature = temperature if temperature is not None else self.random_temp(0.1, 0.5)
        context_len = max(self.min_context_len, min(len(message) // 3, int(context_length)))
        message = self.to_msgs(message) if name.startswith('gpt') else message
        return message, name, stream, temperature, context_len, num_predict, aggregation_method

    def prep_context(self, *args, name:str, **kwargs, ) -> dict:
        """
        Prepares the context based on the method name and model.
        """
        messages, name, stream, temperature, context_len, num_predict, aggregation_method = \
                                            self.get_params(*args, name=name, **kwargs)
        # we create a context dictionary with model parameter
        # context len is calculated dynamically in a range between 2000 and context_lenght
        context = {'model': name, 'stream': stream}
        if name.startswith('gpt'):
            context['messages'] = messages
            context['temperature'] = temperature
        else:
            context['prompt'] = messages
            context['options'] = {  'temperature': temperature,
                                    'num_ctx': context_len,
                                }
            if num_predict is not None: 
                context['options']['num_predict'] = num_predict
            context['aggregation_method'] = aggregation_method
            context['keep_alive'] = msts.config.defaults.get('keep_alive')
        # keep_alive seems to be in seconds (docs say minutes)
        return context

    def set_sub_domain(self, *args, sub_domain:str=None, **kwargs) -> str:
        # if no sub-domain is specified we get it from default params
        if sub_domain is None:
            sub_domain = msts.config.defaults.get('sub_domain')
        return sub_domain


    def post(self, *args, **kwargs) -> dict:
        """
        Sends a message to the appropriate assistant and handles the response.
        """
        kwargs['sub_domain'] = self.set_sub_domain(*args, **kwargs)
        # method names may only use underscore
        return getattr( self, self.method_name_from_server(*args, **kwargs)
                        )(  self.prep_context(*args,
                                **msts.config.get_model(*args, **kwargs).get('model_file'), 
                                **kwargs,
                            ), *args, **kwargs 
                            )

    def method_name_from_server(self, *args, **kwargs):
        return (
                msts.config.get_model(*args, **kwargs).get('server')
                .split('_')[0].replace('-', '_')
                )

    def while_ai(self, context: dict, *args, **kwargs, ) -> dict:
        """
        Handles communication with a custom AI assistant.
        sub_domain: str, ['get_embeddings', 'generate']
        """
        # we are sending the request to the server
        print(f"{context = }")
        print(f"URL: {msts.config.get_url(*args, **kwargs)}")
        r = requests.post(  
                            msts.config.get_url(*args, **kwargs),
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps(context),
        )
        r.raise_for_status()
        outs = r.json()
        for i, out in enumerate(outs.get('results')):
            # out['response'] = out.get('response', out.get('embedding'))
            out['num_results'] = len(outs.get('results'))
        return outs

    def openAI(self, context: dict, *args, **kwargs) -> dict:
        """
        Handles communication with the OpenAI assistant.
        """
        self.client = OpenAI(api_key=msts.config.api_key)
        response = self.client.chat.completions.create(**context).choices[0].message.__dict__
        return response