# assistant.py

import altered.model_params as msts
import altered.hlp_printing as hlpp
import altered.settings as sts
from typing import Dict, Union, Tuple
from openai import OpenAI
import json, re, requests, time
from colorama import Fore, Style, Back
import random as rd
import math
from datetime import datetime as dt
import warnings
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
        self.columns = [
            'network_up_time', 'server_time', 'network_down_time', 'total_time',
            'time_stamp', 'api_counter', 'prompt_counter', 'num_ctx_prompt',
            'num_ctx_response', 'server', 'model'
        ]
        # Create an initial DataFrame with one row filled with None values and an index of [0]
        self.times_df = pd.DataFrame([{col: None for col in self.columns}], index=[0])

    @staticmethod
    def set_rd_temp(lower:float=None, upper:float=None, temp:float=None, scale:int=1, 
        verbose:int=0, **kwargs ) -> float:
        if temp is not None:
            return temp
        bias = math.log(scale, 1000)
        lower = (0.1 + bias) if lower is None else (lower + bias)
        upper = (0.1 + bias) if upper is None else (upper + bias)
        rd_temp = min(max(lower, rd.random()), upper)
        if verbose:
            print(  f"{Fore.YELLOW}Warning: set_rd_temp setting temperature:{Fore.RESET} "
                    f"temp: {rd_temp:.2f}, {bias = }, {scale = }")
        return rd_temp

    def get_context_length(self, messages:[str, list], context_length:int, *args, **kwargs
        ) -> int:
        # we estimate the context length based on the messages length
        # num_ctx will be get_num_ctx for the longest message in messages
        num_ctx = max(max([len(msg) // 3 for msg in messages]), self.min_context_len)
        # if num_ctx is larger than we print an alert
        if num_ctx > context_length:
            print(
                f"{Fore.YELLOW}WARNING{Fore.RESET}: "
                f"num_ctx: {Fore.YELLOW}{num_ctx}{Fore.RESET} is greater than "
                f"context_length: {Fore.YELLOW}{context_length}{Fore.RESET}. "
                f"Setting num_ctx to context_length."
                )
        num_ctx = min(num_ctx, context_length)
        return num_ctx


    def get_params(self, messages:[str, list], *args, service_endpoint:str,
                                                        name:str,
                                                        context_length:int,
                                                        temperature:float=None,
                                                        num_predict:int=None,
                                                        repeats:int=sts.repeats,
                                                        fmt:str='markdown',
                                                        prompt_summary:dict=None,
                                                        **kwargs,
        ) -> dict:
        # print(f"{Fore.YELLOW}service_endpoint:{Fore.RESET} {service_endpoint}")
        if service_endpoint in ['get_embeddings', 'get_generates']:
            # for embeddings and generate[s]! messages is a list, to allow for 
            # multiple messages to be embedded with a single server call
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
        temperature = ModelConnect.set_rd_temp(0.1, 0.5, temperature, repeats['num'], **kwargs)
        # we estimate the context length based on the messages length
        num_ctx = self.get_context_length(messages, context_length, *args, **kwargs)
        messages = self.to_msgs(messages) if name.startswith('gpt') else messages
        return fmt, messages, name, temperature, num_ctx, num_predict,\
                     repeats, service_endpoint, prompt_summary

    def prep_context(self, *args, name:str, verbose:int=0, **kwargs, ) -> dict:
        """
        Prepares the context based on the method name and model.
        """
        fmt, messages, name, temperature, num_ctx, num_predict,\
        repeats, service_endpoint, prompt_summary = \
                     self.get_params(*args, name=name, **kwargs)
        # we create a context dictionary with model parameter
        # context len is calculated dynamically in a range between 2000 and context_lenght
        context = {'model': name,}
        if name.startswith('gpt'):
            context['messages'] = messages
            context['messages'][0]['content'] = "\n".join(messages[0]['content'])
            context['temperature'] = temperature
        else:
            context['verbose'] = verbose
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
                    # num_predict is also used by server_ollama_endpoint, so we add it here to
                    context['num_predict'] = num_predict
                context['fmt'] = fmt
                context['stream'] = False
                context['repeats'] = repeats
                context['prompt_summary'] = prompt_summary
        # print(f"{Fore.YELLOW}ModelConnect.prep_context.context:{Fore.RESET} \n{context}")
        # keep_alive seems to be in seconds (docs say minutes)
        return context

    def post(self, *args, **kwargs) -> dict:
        """
        Sends a message to the appropriate assistant and handles the response.
        """
        m_params = msts.config.get_model(*args, **kwargs)
        context = self.prep_context(*args, **m_params.get('model_file'), **kwargs)
        response = self.call_model(m_params, context, *args, **kwargs)
        self.validate_response(response, *args, **kwargs)
        if not m_params.get('model_file').get('name').startswith('gpt'):
            self.get_stats(response, context, *args, **kwargs)
        return response

    def call_model(self, m_params, context, *args, **kwargs) -> dict:
        self.print_calling_params(m_params, context, *args, **kwargs)
        # chat-gpt and ollama use different methods in this class which are defined
        # by the model_file['host'] key in the models_servers.yml file
        response = getattr(self, m_params['model_file']['host'])(m_params.get('url'), context)
        # we append some parameter context for documentation purposes
        response['model'] = m_params.get('model_file').get('name')
        response['server'] = m_params.get('server')
        return response

    def print_calling_params(self, m_params, context, *args, fmt, verbose, **kwargs):
        if verbose:
            m_func = m_params['model_file']['host']
            print(  f"{Fore.MAGENTA}ModelConnect.post {m_func}: {Fore.RESET}\n"
                    f"\tmodel={context['model']}, "
                    f"server={m_params.get('server')}, "
                    f"url={m_params.get('url')}, \n"
                    f"\trepeats={context.get('repeats', 'no repeats for embeddings')}, "
                    f"num_prompts={len(context.get('prompts', []))}\n"
                    f"\t{fmt = }, num_predict={context.get('options')}\n"
                    f"\t{verbose = } >= 1 \n"
                        )
        elif verbose >= 2:
            hlpp.unroll_print_dict(context, 'context')

    def _ollama(self, url, context: dict) -> dict:
        """
        Handles communication with a custom AI assistant.
        service_endpoint: str, ['get_embeddings', 'generate']
        """
        # we are sending the request to the server
        context['network_up_time'] = time.time()
        try:
            r = requests.post(  url,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(context),
            )
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}ModelConnect._ollama Error!"
                  f"\nNOTE: {msts.config.used_defaults = } "
                  f"might be the cause of the error.{Fore.RESET}")
            raise e
        r.raise_for_status()
        response = r.json()
        response['num_results'] = len(response['responses'])
        return response

    def openAI(self, _, context: dict) -> dict:
        """
        Handles communication with the OpenAI assistant.
        """
        self.client = OpenAI(api_key=msts.config.api_key)
        response = self.client.chat.completions.create(**context).choices[0].message.__dict__
        # we harmonize the response data struture for latter processing
        response = {'responses': [{'response': response['content']}]}
        return response

    def validate_response(self, r_dict:dict, *args, verbose:int=0, **kwargs) -> bool:
        # the response might contain model errors such as 'error': 'Model not found'
        if verbose >= 2:
            # we shorten the 'context' in response because it contains token ids
            print_dict = self.shorten_context(r_dict)
            print(f"\n{Fore.MAGENTA}ModelConnect.validate_response:{Fore.RESET}")
            hlpp.unroll_print_dict(print_dict, 'print_dict')
        for response in r_dict['responses']:
            if 'error' in response:
                if re.match(r"model '.*' not found", response['error']):
                    raise ValueError( 
                            f"{Fore.RED}Error in response: {response['error']}{Fore.RESET} "
                            f"{Fore.RED}Check model name for this server {Fore.RESET}"
                            f"{Fore.RED}in models_servers.yml{Fore.RESET}"
                            )

    def shorten_context(self, r_dict:dict) -> dict:
        """
        We shorten the 'context' key in the response dictionary because it contains token ids.
        """
        print_dict = r_dict.copy()
        for resp in print_dict['responses']:
            if 'context' in resp:
                num_tokens = len(resp['context'])
                resp['context'] = f"{resp['context'][:3]}".replace(']', f', {num_tokens = }]')
        return print_dict

    def get_stats(self, r, context, *args, context_length: int = 8000, verbose: int = 0, 
        **kwargs) -> dict:
        """
        We add the current model times to the total times.
        We create a pandas dataframe containing all times for each call of get_stats.
        Also, we calculate and update the cumulative times at each call.
        """
        # Calculate network times
        r['network_down_time'] = time.time() - r['network_down_time']
        time_delta = (r['network_down_time'] - r['network_up_time']) / 2
        r['network_up_time'] += time_delta
        r['network_down_time'] -= time_delta
        r['total_time'] = r['network_down_time'] + r['network_up_time'] + r['server_time']
        # Prepare the new record for the current stats
        r['num_ctx_prompt'] = context['options']['num_ctx']
        all_responses = [resp.get('response', []) for resp in r.get('responses', [])]
        r['num_ctx_response'] = self.get_context_length(all_responses, context_length)
        r['time_stamp'] = dt.now()
        # Update the cumulative times
        for col in self.times: self.times[col] += r.get(col, 0)
        # Overwrite the last row (totals row) with the new record
        self.times_df.iloc[-1] = {k: r.get(k, None) for k in self.columns}
        # Update cumulative times row directly as the new last row
        self.times_df.loc[len(self.times_df)] = {col: self.times.get(col, 0) 
                                                                    for col in self.columns}
        if verbose:
            print(f"\n{Fore.MAGENTA}ModelConnect.get_stats:{Fore.RESET}")
            hlpp.pretty_print_df(self.times_df, *args, sum_color=Fore.MAGENTA, **kwargs)


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