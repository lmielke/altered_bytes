# assistant.py

import altered.model_params as msts
import altered.settings as sts
from typing import Dict, Union, Tuple
from openai import OpenAI
import json, re, requests, time
from colorama import Fore, Style
import random as rd
import math

class ModelConnect:
    """
    ModelConnect handles the communication with an AI assistant of your choice.
    For some assistants, Ollama is currently hosting and running the models. 
    See model_settings.models for the assistants and their respective models.
    The remote Ollama machines are listening on 0.0.0.0:11434 and are accessible 
    via the local private Network.
    On how to use see project_dir/altered/test/test_ut/test_assistant.py
    """

    def __init__(self, *args, **kwargs) -> None:
        self.min_context_len = 2000
        self.to_msgs = lambda msg: [{'role': 'user', 'content': msg}]
        self.times = {
                        'network_up_time': 0.0, 
                        'network_down_time': 0.0, 
                        'total_server_time': 0.0,
                        }

    @staticmethod
    def set_rd_temp(lower:float=None, upper:float=None, temp:float=None, scale:int=1) -> float:
        if temp is not None:
            return temp
        bias = math.log(scale, 1000)
        lower = (0.1 + bias) if lower is None else (lower + bias)
        upper = (0.1 + bias) if upper is None else (upper + bias)
        rd_temp = min(max(lower, rd.random()), upper)
        print(f"{Fore.YELLOW}Warning: {Fore.RESET}temp: {rd_temp:.2f}, {bias = }, {scale = }")
        return rd_temp

    def get_params(self, message:[str, list], *args, service_endpoint:str,
                                                        name:str,
                                                        context_length:int,
                                                        temperature:float=None,
                                                        num_predict:int=None,
                                                        repeats:int=sts.repeats,
                                                        fmt:str='markdown',
                                                        **kwargs,
        ) -> dict:
        # print(f"{Fore.YELLOW}service_endpoint:{Fore.RESET} {service_endpoint}")
        if service_endpoint in ['get_embeddings', 'get_generates']:
            # for embeddings and generate[s]! message is a list, to allow for multiple messages to be embedded
            # with a single server call
            msg = ( 
                    f"{Fore.YELLOW}WARNING{Fore.RESET}: "
                    f"Expected message to be a list, "
                    f"but got {Fore.YELLOW}{type(message)}{Fore.RESET} instead.\n"
                    f"Converting to List"
                    )
            if type(message) != list:
                message = [str(message)]
            # for embeddings we want the temperature to be low to be more deterministic
            if service_endpoint == 'get_embeddings':
                temperature = 0.
        # repeats refers to the number of times the prompt is repeated
        # we increase the temperature for repeats > 1 to get more diverse responses
        temperature = ModelConnect.set_rd_temp(0.1, 0.5, temperature, repeats['num'])
        # we estimate the context length based on the message length
        num_ctx = max(self.min_context_len, min(len(message) // 3, int(context_length)))
        messages = self.to_msgs(message) if name.startswith('gpt') else message
        return fmt, messages, name, temperature, num_ctx, num_predict,\
                     repeats, service_endpoint

    def prep_context(self, *args, name:str, **kwargs, ) -> dict:
        """
        Prepares the context based on the method name and model.
        """
        fmt, messages, name, temperature, num_ctx, num_predict,\
        repeats, service_endpoint = \
                     self.get_params(*args, name=name, **kwargs)
        # we create a context dictionary with model parameter
        # context len is calculated dynamically in a range between 2000 and context_lenght
        context = {'model': name,}
        if name.startswith('gpt'):
            context['messages'] = messages
            context['temperature'] = temperature
        else:
            context['service_endpoint'] = msts.config.defaults.get('service_endpoint') \
                                            if service_endpoint is None else service_endpoint
            context['prompts'] = messages
            context['keep_alive'] = msts.config.defaults.get('keep_alive')
            context['options'] = {  
                                    'temperature': temperature,
                                    'num_ctx': num_ctx,
                                }
            if context.get('service_endpoint') == 'get_generates':
                if num_predict is not None: 
                    context['options']['num_predict'] = num_predict
                    # num_predict is also used by pre_ollama_server, so we add it here to
                    context['num_predict'] = num_predict
                context['fmt'] = fmt
                context['stream'] = False
                context['repeats'] = repeats
        # print(f"{Fore.YELLOW}ModelConnect.prep_context.context:{Fore.RESET} \n{context}")
        # keep_alive seems to be in seconds (docs say minutes)
        return context

    def set_service_endpoint(self, *args, service_endpoint:str=None, **kwargs) -> str:
        # if no sub-domain is specified we get it from default params
        if service_endpoint is None:
            service_endpoint = msts.config.defaults.get('service_endpoint')
        return {'service_endpoint': service_endpoint}


    def post(self, *args, **kwargs) -> dict:
        """
        Sends a message to the appropriate assistant and handles the response.
        """
        kwargs.update(self.set_service_endpoint(*args, **kwargs))
        # print(f"model_connect.post: {kwargs = }")
        # print(msts.config.get_model(*args, **kwargs).get('model_file'))
        r = self.ollama(self.prep_context(*args,
                                **msts.config.get_model(*args, **kwargs).get('model_file'), 
                                **kwargs,
                            ), *args, **kwargs 
                            )
        r['model'] = msts.config.get_model(*args, **kwargs).get('model_file').get('name')
        self.get_stats(r, *args, **kwargs)
        return r

    def get_stats(self, r, *args, **kwargs) -> dict:
        """
        we add the current model times  to the total times
        """
        r['network_down_time'] += -time.time()
        self.times = {k: float(f"{self.times.get(k, 0.0) + float(vs):.3f}")
                                                for k, vs in r.items() if k in self.times}

    def ollama(self, context: dict, *args, **kwargs, ) -> dict:
        """
        Handles communication with a custom AI assistant.
        service_endpoint: str, ['get_embeddings', 'generate']
        """
        # we are sending the request to the server
        context['network_up_time'] = time.time()
        # print(f"model_connect.ollama.url: {msts.config.get_url(*args, **kwargs)}")
        # print(f"model_connect.ollama.context: {context}")
        r = requests.post(  
                            msts.config.get_url(*args, **kwargs),
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps(context),
        )
        r.raise_for_status()
        r_dict = r.json()
        for i, (field, response) in enumerate(r_dict.copy().items()):
            r_dict['num_results'] = len(r_dict)
        return r_dict

    def openAI(self, context: dict, *args, **kwargs) -> dict:
        """
        Handles communication with the OpenAI assistant.
        """
        self.client = OpenAI(api_key=msts.config.api_key)
        response = self.client.chat.completions.create(**context).choices[0].message.__dict__
        return response