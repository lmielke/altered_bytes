# assistant.py

import altered.model_params as msts
import altered.settings as sts
from typing import Dict, Union, Tuple
from openai import OpenAI
import json, re, requests, time
from colorama import Fore, Style
import random as rd
import math
from datetime import datetime as dt
import pandas as pd

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
                        'server_time': 0.0,
                        'total_time': 0.0,
                        }
        self.columns = ['network_up_time', 'server_time', 'network_down_time', 'total_time',
                        'time_stamp', 'api_counter', 'prompt_counter', 'num_ctx_prompt',
                        'num_ctx_response']
        self.times_df = pd.DataFrame(columns=self.columns)

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

    def get_context_length(self, messages:[str, list], context_length:int, *args, **kwargs) -> int:
        # we estimate the context length based on the messages length
        # num_ctx will be get_num_ctx for the longest message in messages
        num_ctx = max(max([len(msg) // 3 for msg in messages]), self.min_context_len)
        # if num_ctx is larger than we print an alert
        if num_ctx > context_length:
            print(
                f"{Fore.RED}ERROR{Fore.RESET}: "
                f"num_ctx: {Fore.YELLOW}{num_ctx}{Fore.RESET} is greater than "
                f"context_length: {Fore.YELLOW}{context_length}{Fore.RESET}. "
                f"Setting num_ctx to context_length."
                )
            exit()
        num_ctx = min(num_ctx, context_length)
        return num_ctx


    def get_params(self, messages:[str, list], *args, service_endpoint:str,
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
            # for embeddings and generate[s]! messages is a list, to allow for multiple messages to be embedded
            # with a single server call
            msg = ( 
                    f"{Fore.YELLOW}WARNING{Fore.RESET}: "
                    f"Expected messages to be a list, "
                    f"but got {Fore.YELLOW}{type(messages)}{Fore.RESET} instead.\n"
                    f"Converting to List"
                    )
            if type(messages) != list:
                messages = [str(messages)]
            # for embeddings we want the temperature to be low to be more deterministic
            if service_endpoint == 'get_embeddings':
                temperature = 0.
        # repeats refers to the number of times the prompt is repeated
        # we increase the temperature for repeats > 1 to get more diverse responses
        temperature = ModelConnect.set_rd_temp(0.1, 0.5, temperature, repeats['num'])
        # we estimate the context length based on the messages length

        num_ctx = self.get_context_length(messages, context_length, *args, **kwargs)
        messages = self.to_msgs(messages) if name.startswith('gpt') else messages
        return fmt, messages, name, temperature, num_ctx, num_predict,\
                     repeats, service_endpoint

    def prep_context(self, *args, name:str, verbose:int=0, **kwargs, ) -> dict:
        """
        Prepares the context based on the method name and model.
        """
        fmt, messages, name, temperature, num_ctx, num_predict,\
        repeats, service_endpoint = \
                     self.get_params(*args, name=name, **kwargs)
        # we create a context dictionary with model parameter
        # context len is calculated dynamically in a range between 2000 and context_lenght
        context = {'model': name, 'verbose': verbose}
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
        context = self.prep_context(*args,
                                **msts.config.get_model(*args, **kwargs).get('model_file'), 
                                **kwargs,
                            )
        r = self.ollama(context, *args, **kwargs )
        r['model'] = msts.config.get_model(*args, **kwargs).get('model_file').get('name')
        self.get_stats(r, context, *args, **kwargs)
        return r

    def get_stats(self, r, context, *args, context_length:int=2000, **kwargs) -> dict:
        """
        we add the current model times  to the total times
        we create a pandas dataframe containing all times for each call of get_stats
        also we calculate and update the cumulative times at each call
        """
        r['network_down_time'] = time.time() - (r['network_down_time'])
        time_delta = (r['network_down_time'] - r['network_up_time']) / 2
        r['network_up_time'] += time_delta
        r['network_down_time'] -= time_delta
        r['total_time'] = r['network_down_time'] + r['network_up_time'] + r['server_time']
        for col in self.times:
            self.times[col] += r.get(col)
        # we append the times to self.times_df
        r['time_stamp'] = dt.now()
        r['num_ctx_prompt'] = context['options']['num_ctx']
        all_responses = [resp.get('response', []) for resp in r.get('responses')]
        r['num_ctx_response'] = self.get_context_length(all_responses, context_length)
        # Convert the dictionary into a DataFrame and add it as a row
        record_df = pd.DataFrame([{k: r[k] for k in self.columns}], columns=self.columns)
        summary_df = pd.DataFrame([self.times], columns=self.columns)
        # Use pd.concat to add the new row to the DataFrame
        self.times_df = pd.concat([self.times_df.iloc[:-1], record_df], ignore_index=True)
        self.times_df = pd.concat([self.times_df, summary_df], ignore_index=True)
        print(f"\n{Fore.CYAN}self.times_df:{Fore.RESET} \n{self.times_df}")



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

class SingleModelConnect(ModelConnect):
    """
    SingleModelConnect is a singleton subclass of ModelConnect that ensures only one instance 
    of the model configuration parameters is created. 
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingleModelConnect, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not self._initialized:
            super().__init__(*args, **kwargs)
            self._initialized = True