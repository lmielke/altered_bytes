from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import math, random as rd, json, re, requests, time
from datetime import datetime as dt
import pandas as pd

import altered.model_params as msts
import altered.hlp_printing as hlpp
import altered.settings as sts
from openai import OpenAI
from colorama import Fore, Style, Back


@dataclass
class ConParams:
    """
    Dataclass encapsulating all parameter and context settings for a model API call.
    """
    model:              str
    messages:           Optional[Any] = None # prompts or messages
    # optins is a nested dict with multiple elements (temperature, num_ctx, num_predict)
    options:            Dict[str, Any] = field(init=False, default_factory=dict)
    temperature:        Optional[float] = None
    num_ctx:            Optional[int] = None
    num_predict:        Optional[int] = None
    keep_alive:         Optional[int] = 200
    service_endpoint:   Optional[str] = None
    stream:             Optional[bool] = False
    # helper parameters
    context_length:     int = 8000
    repeats:            Dict[str, Any] = field(default_factory=lambda: sts.repeats)
    fmt:                str = 'markdown'
    prompt_summary:     Optional[Dict] = None
    verbose:            int = 0

    def __post_init__(self, *args, **kwargs) -> None:
        # Normalize messages for GPT-based models.
        if self.messages is None:
            self.messages = []
        if self.model.startswith('gpt'):
            if not isinstance(self.messages, list):
                self.messages = [str(self.messages)]
            self.messages = [
                msg if isinstance(msg, dict)
                else {'role': 'user', 'content': str(msg)}
                for msg in self.messages
            ]
            if self.messages and isinstance(self.messages[0].get('content'), list):
                self.messages[0]['content'] = "\n".join(self.messages[0]['content'])
        # Set temperature.
        self.temperature = self._set_rd_temp(
            lower=0.1,
            upper=0.5,
            temp=self.temperature,
            scale=self.repeats.get('num', 1),
            verbose=self.verbose,
            *args, **kwargs
        )
        # Compute effective context length.
        self.num_ctx = self._compute_num_ctx(self.context_length, default_min=2000)
        self.options = {'temperature': self.temperature, 'num_ctx': self.num_ctx}
        # Set a default service_endpoint if none provided.
        if not self.service_endpoint:
            self.service_endpoint = msts.config.defaults.get('service_endpoint')

    @staticmethod
    def _set_rd_temp(lower: float, upper: float, temp: Optional[float],
                     scale: int, verbose: int = 0, *args, **kwargs) -> float:
        """Return provided temperature or generate a bounded random temperature."""
        if temp is not None:
            return temp
        bias = math.log(scale, 1000)
        lower = (0.1 + bias) if lower is None else (lower + bias)
        upper = (0.1 + bias) if upper is None else (upper + bias)
        rd_temp = min(max(lower, rd.random()), upper)
        if verbose:
            print(f"{Fore.YELLOW}Warning: setting temperature to {rd_temp:.2f} "
                  f"with bias {bias} and scale {scale}{Fore.RESET}")
        return rd_temp

    def _compute_num_ctx(self, context_length: int, default_min: int = 2000) -> int:
        """Estimate context length based on message sizes."""
        lengths = []
        for msg in self.messages:
            content = (msg.get('content') if isinstance(msg, dict) and 'content' in msg
                       else str(msg))
            lengths.append(len(content) // 3)
        num_ctx = max(max(lengths) if lengths else default_min, default_min)
        if num_ctx > context_length:
            print(f"{Fore.YELLOW}WARNING{Fore.RESET}: Computed num_ctx "
                  f"({num_ctx}) exceeds context_length ({context_length}); "
                  f"using context_length instead.")
        return min(num_ctx, context_length)

    def to_dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Convert the ConParams instance into the dictionary required by the API."""
        context = {'model': self.model, 'temperature': self.temperature, }
        if self.model.startswith('gpt'):
            context['messages'] = self.messages
        else:
            context['prompts'] = self.messages
            context['options'] = self.options
            context['fmt'] = self.fmt
            context['verbose'] = self.verbose
            context['network_up_time'] = time.time()
            if self.service_endpoint:
                context['service_endpoint'] = self.service_endpoint
            if self.prompt_summary:
                context['prompt_summary'] = self.prompt_summary
            if self.repeats:
                context['repeats'] = self.repeats
            if self.num_predict is not None:
                context['num_predict'] = self.num_predict
        return context


class ModelConnect:
    """
    Handles the connection to the remote AI assistant.
    This class is very stripped down. It uses composition with ConParams to handle
    parameter configuration and ModelStats for tracking statistics.
    Example:
        from altered.model_connect import ModelConnect
        messages = ['Why is the sky blue?']
        alias = 'l3.2_1'
        ModelConnect().post(*args, messages=messages, alias=alias, **kwargs)

    """
    def __init__(self, *args, **kwargs) -> None:
        self.stats = ModelStats(*args, **kwargs)
        self.m_params: Mandatory[Dict[str, Any]] = {}

    def post(self, *args, **kwargs) -> dict:
        """
        Sends a message to the remote AI assistant and returns the response.
        """
        try:
            self.m_params = msts.config.get_model(*args, **kwargs)
            self.print_connect_params(*args, **kwargs)
        except Exception as e:
            print(f"{Fore.RED}ModelConnect.post prep_params Error!\n{e}{Fore.RESET}")
            raise
        try:
            response = RmConnect()( *args,
                                        func=self.m_params['model_file']['host'],
                                        name=self.m_params['model_file']['name'],
                                        url=self.m_params['url'],
                                    **kwargs
                                    )
            response['model'] = self.m_params['model_file']['name']
            response['server'] = self.m_params.get('server')
        except Exception as e:
            print(f"{Fore.RED}ModelConnect.post RmConnect Error!\n{e}{Fore.RESET}")
            raise
        try:
            self.validate_response(response, *args, **kwargs)
        except Exception as e:
            print(f"{Fore.RED}ModelConnect.post validate_response Error!\n{e}{Fore.RESET}")
            raise
        try:
            self.stats(response, *args, model=self.m_params['model_file']['name'], **kwargs)
        except Exception as e:
            print(f"{Fore.RED}ModelConnect.post stats Error!\n{e}{Fore.RESET}")
            raise
        return response

    def validate_response(self, r_dict: dict, *args, verbose: int = 0, **kwargs) -> bool:
        """
        Validates the response from the model API call.
        """
        for response in r_dict.get('responses', []):
            if 'error' in response:
                if re.match(r"model '.*' not found", response['error']):
                    raise ValueError(f"{Fore.RED}Error in response: {response['error']}"
                                     f"{Fore.RESET}")
        return True

    def print_connect_params(self, *args, fmt:str=None, verbose:int=0, **kwargs):
        """
        Prints parameters and context for debugging purposes.
        """
        if verbose:
            print(  
                    f"{Fore.MAGENTA}ModelConnect.post {self.m_params['model_file']['host']}: "
                    f"{Fore.RESET}\n"
                    f"\tserver={self.m_params.get('server')}\n"
                    f"\turl={self.m_params.get('url')}\n"
                    f"\t{fmt = }, {verbose = }")
        elif verbose >= 2:
            hlpp.unroll_print_dict(ctx, 'context', *args, **kwargs)

class RmConnect:

    def __call__(self, *args, func:str, name:str, **kwargs) -> dict:
        """
        Dispatch the model call according to the given parameters.
        """
        ctx = self.mk_context(*args, model=name, **kwargs)
        self.print_calling_params(func, *args, ctx=ctx, **kwargs)
        # Call the appropriate model function.
        response = getattr(self, func)(*args, ctx=ctx, **kwargs)
        return response

    def mk_context(self, messages, *args, model:str, verbose:int=0, **kwargs) -> None:
        # Set up the context with model parameters.
        try:
            return ConParams(   *args,
                                messages=messages,
                                model=model, 
                                verbose=verbose,
                                # we filter for the parameters available in ConParams
                                **{k: v for k, v in kwargs.items() 
                                        if k in set(ConParams.__dataclass_fields__.keys())}
                    ).to_dict(*args, **kwargs)
        except Exception as e:
            print(f"{Fore.RED}RmConnect.prep_params Error!\n{e}{Fore.RESET}")
            raise

    def print_calling_params(self, func, *args, url:str, ctx:dict, verbose:int=0, **kwargs):
        """
        Prints parameters and context for debugging purposes.
        """
        if verbose:
            print(f"{Fore.MAGENTA}RmConnect.post {func}, {url = }: {Fore.RESET}\n"
                  f"\tmodel={ctx['model']},  "
                  f"repeats={ctx.get('repeats', 'N/A')}, "
                  f"num_prompts={len(ctx.get('prompts', []))} "
                  f"num_predict={ctx.get('options')}, "
                  )
        elif verbose >= 2:
            hlpp.unroll_print_dict(ctx, 'context', *args, **kwargs)

    @staticmethod
    def _ollama(*args, url:str, ctx:dict, **kwargs) -> dict:
        """
        Internal method to send a request to an Ollama-hosted model.
        Example python:
            from altered.model_connect import RmConnect
            url = 'http://192.168.0.235:5555/api/get_generates'
            ctx = {
                        "model": "llama3.2:3b",
                        "temperature": 0.5,
                        "prompts": ["Why is the sky blue?"],
                        "options": {"temperature": 0.5, "num_ctx": 2000},
                        "fmt": "markdown",
                        "verbose": 3,
                        "network_up_time": 1744625021.660603,
                        "service_endpoint": "get_generates",
                        "prompt_summary": "Why is the sky blue?",
                        "repeats": {"num": 1, "agg": None},
                        "num_predict": 500
                    }
            RmConnect._ollama(url=url, ctx=ctx)
        
        Example curl:
            $url = "http://192.168.0.245:5555/api/get_generates"
            $ct = "application/json"
            # Create a JSON object with the message
            $context = @{
                        model = 'llama3.2'
                        prompts = @($Msg)
                        options = @{
                                        temperature = 0.1
                                        num_ctx = 8000
                                        num_predict = 100
                        }
                        keep_alive = 200
                        service_endpoint = 'get_generates'
                        stream = $false
                        network_up_time = 0.0
            } | ConvertTo-Json            
            # Send the request
            $response = Invoke-RestMethod -Method Post -Uri $url -Body $context -ContentType $ct
            return $response[0].responses.response
        """
        try:
            r = requests.post(url,
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(ctx),
                              )
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}RmConnect._ollama Error!{Fore.RESET}")
            raise e
        r.raise_for_status()
        response = r.json()
        response['num_results'] = len(response.get('responses', []))
        response['num_ctx_pr'] = ctx.get('options', {}).get('num_ctx', 0)
        return response

    def openAI(self, *args, ctx:dict, **kwargs) -> dict:
        """
        Handles communication with the OpenAI assistant.
        """
        client = OpenAI(api_key=msts.config.api_key)
        response = client.chat.completions.create(**ctx).choices[0].message.__dict__
        return {'responses': [{'response': response['content']}]}

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


class ModelStats:
    """
    Encapsulates timing statistics and logging for model calls.
    """
    def __init__(self, *args, columns: Optional[List[str]] = None, **kwargs) -> None:
        self.times = {
            'network_up_time': 0.0,
            'network_down_time': 0.0,
            'server_time': 0.0,
            'total_time': 0.0,
        }
        self.columns = columns or [
            'network_up_time', 'server_time', 'network_down_time', 'total_time',
            'time_stamp', 'api_counter', 'prompt_counter', 'num_ctx_pr',
            'num_ctx_resp', 'server', 'model'
        ]
        self.times_df = pd.DataFrame([{col: None for col in self.columns}], index=[0])

    def __call__(self, r:dict, *args, model:str, **kwargs) -> dict:
        if model.startswith('gpt'):
            return r
        return self.update_stats(r, *args, **kwargs)

    def update_stats(self, r: dict, *args, context_length: int = 8000,
                     verbose: int = 0, **kwargs) -> dict:
        """Update timing stats based on the response and context."""
        r['network_down_time'] = time.time() - r.get('network_down_time', time.time())
        time_delta = (r['network_down_time'] - r.get('network_up_time', 0)) / 2
        r['network_up_time'] = r.get('network_up_time', 0) + time_delta
        r['network_down_time'] -= time_delta
        r['total_time'] = (         r['network_down_time'] +
                                    r.get('network_up_time', 0) +
                                    r.get('server_time', 0)
        )
        all_responses = [resp.get('response', []) for resp in r.get('responses', [])]
        r['num_ctx_resp'] = (max(len(resp) // 3 for resp in all_responses)
                             if all_responses else 0)
        r['time_stamp'] = dt.now().strftime("%H:%M")
        for col in self.times:
            self.times[col] += r.get(col, 0)
        self.times_df.iloc[-1] = {k: r.get(k, None) for k in self.columns}
        self.times_df.loc[len(self.times_df)] = {col: self.times.get(col, 0)
                                                  for col in self.columns}
        if verbose:
            hlpp.pretty_print_df(self.times_df, *args, sum_color=Fore.MAGENTA, **kwargs)
        return r
