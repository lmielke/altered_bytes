import json
import os
import time
import yaml
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from ollama import Client
from colorama import Fore, Style

import altered.model_params as msts
import altered.settings as sts
from altered.prompt_instructs import Instructions
from altered.renderer import Render


class PromptStrategies:
    strategy = 'prompt_aggregations'

    def __init__(self, *args, **kwargs):
        self.inst = Instructions(*args, **kwargs)
        self.renderer = Render(*args, **kwargs)
        self.pr_strategies = self.inst.get_strategy(strategy = 'prompt_aggregations')

    def load_strategies(self, strategy, *args, **kwargs):
        """
        Loads the service parameters from a YAML file. The file is expected to be 
        located under 'resources/strategies/' relative to the script's directory.
        """
        params_dir = os.path.join(os.path.dirname(__file__), 'resources', 'strategies')
        with open(os.path.join(params_dir, f"{strategy}.yml"), 'r') as file:
            return yaml.safe_load(file)

    def get_strategy(self, *args, strategy:str=None, **kwargs):
        if strategy is None: return ''
        if '.' in strategy:
            strat_group, strat_name = strategy.split('.')
        else:
            strat_group, strat_name = strategy, 'max'
        return self.pr_strategies.get(strat_group).get(strat_name), strat_name

    def mk_agg_prompt(self, prompts:list, responses:list, *args, fmt:str=None, **kwargs) -> dict:
        """
        Generates a prompt based on the specified strategy.
        """
        strats, strat_name = self.get_strategy(*args, **kwargs)
        sample_pairs = [
                            f"Prompt {i+1}: {prompt}\nResponse {i+1}: {resp}"
                            for i, (prompt, resp) in enumerate(zip(prompts, responses))
        ]
        samples_section = "<samples>\n" + "\n\n".join(sample_pairs) + "\n</samples>"
        if fmt is not None:
            format_instruct = f"Provide your answer in {fmt}!"
        new_prompt = (
                        f"\n## Below are {len(prompts)} samples of an LLM's Response.\n"
                        f"{samples_section}\n"
                        f"{' '.join(strats.values())}"
                        f"\n{format_instruct}"
        )
        context = {'number_of': len(prompts)}
        return self.renderer.render_from_string(new_prompt, context )


class Endpoints:

    def __init__(self, *args, **kwargs):
        self.ep_mappings = {
                                'get_generates': 'generate', 
                                'get_embeddings': 'embeddings', 
                            }
        self.ollama_params = {'prompt', 'options', 'keep_alive', 'stream', 'model'}
        self.prompt_counter = defaultdict(int)
        self.pr_strat = PromptStrategies(*args, **kwargs)
        self.olc = Client(host='http://localhost:11434')

    def ping(self, *args, server:object, **kwargs) -> dict:
        """
        Generates the JSON response for the /ping request.
        Updates the /ping counter directly.
        """
        # Increment the /ping counter directly
        return {
                    'response': 'pong',
                    'server_ip': server.server_address[0],
                    'server_port': server.server_address[1]
        }

    def get_embeddings(self, ep, *args, prompts:list, **kwargs) -> dict:
        responses = []
        for prompt in prompts:
            responses.append(self._ollama(self.ep_mappings.get(ep), prompt, *args, **kwargs))
        return {'responses': responses}

    def get_generates(self, ep:str, *args, prompts:list, **kwargs) -> dict:
        print(f"get_generates: {prompts = }")
        responses = []
        for prompt in prompts:
            responses.append(self._ollama(self.ep_mappings.get(ep), prompt, *args, **kwargs))
        responses.extend(self.agg_resps(ep, prompts, responses, *args, **kwargs)['responses'])
        return {'responses': responses}

    def agg_resps(self, ep:str, prompts:list, responses:list, *args, 
                                                        strategy:str=None, 
                                                        **kwargs, ):
        """
        Aggregates muliple responses into a single response using the provided 
        aggregation strategy. Also a std is estimated.
        """
        
        aggs = []
        if len(prompts) >= 2 and strategy is not None:
            for strat in [strategy, f"{self.pr_strat.strategy}.std"]:
                if strat.endswith('.std'):
                    kwargs['fmt'] = 'json'
                # creates the prompt for the aggregation
                prompt = self.pr_strat.mk_agg_prompt(
                                                    prompts, 
                                                    [r.get('response') for r in responses], 
                                                    *args, 
                                                    strategy=strat, **kwargs,
                    )
                # here we prompt the model again
                aggs.append(self._ollama(self.ep_mappings.get(ep), prompt, *args, **kwargs))
        return {'responses': aggs}

    def unittest(self, *args, **kwargs) -> dict:
        """
        Generates the JSON response for the /unittest request.
        """
        response = self.ping(*args, **kwargs)
        response.update(self.pr_strat.get_strategy(*args, **kwargs))
        return {'responses': [response]}

    def _ollama(self, func:str, prompt:str, *args, **kwargs) -> dict:
        """
        Generates the JSON response for the /_ollama request.
        """
        # Increment the /_ollama counter directly
        params = {k: vs for k, vs in kwargs.items() if k in self.ollama_params}
        print(f"Ollama: {func = }, {prompt = }, {kwargs = }, {params = }")
        r = getattr(self.olc, func)(prompt=prompt, **params)
        # r = {'model': '_ollama', 'response': 'This is a test response.', 'prompt': prompt, 'params': params}
        return r


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    service = None  # This will be set when the server starts
    allowed_endpoints = {'ping', 'unittest', 'get_generates', 'get_embeddings'}

    def do_POST(self, *args, **kwargs):
        """
        Handles the POST requests by routing to the appropriate service method 
        and sending the response as JSON.
        Tracks the prompt counter and timing information.
        """
        # Update kwargs with the parsed JSON body from the client
        kwargs.update(self.get_kwargs(*args, **kwargs))
        print(f"{kwargs = }")
        self.start_timing(*args, **kwargs)
        ep, payload = self.get_endpoint(*args, **kwargs)
        # Route the request to the appropriate service ep
        payload.update(getattr(self.service, ep)(ep, *args, server=self.server, **kwargs))
        # Update response with timing information and other server statistics
        payload.update(self.end_timing(*args, **kwargs))
        # Send the JSON response
        print(f"do_POST.out: {payload = }")
        self.send_server_response(payload, *args, **kwargs)

    def get_kwargs(self, *args, **kwargs) -> dict:
        return json.loads(self.rfile.read(int(self.headers['Content-Length'])))

    def get_endpoint(self, *args, **kwargs) -> str:
        ep = self.path.strip('/').replace('api/', '')
        if ep not in self.allowed_endpoints:
            time.sleep(2)
            self.send_error(404, f"Not a valid endpoint: '/{ep}'")
            return
        else:
            self.service.prompt_counter[ep] += 1
        print(f"Endpoint: {ep}")
        return ep, {'prompt_counter': self.service.prompt_counter}

    def start_timing(self, *args, network_up_time: float, **kwargs
        ) -> tuple:
        """
        Explicitly handles network_up_time passed from kwargs.
        
        Args:
            start_time: The time when the request started processing.
            network_up_time: The time when the network started, passed from client.
        
        Returns:
            A tuple containing network_up_time and total server time.
        """
        # Calculate elapsed network up time
        time.sleep(0.01)
        self.network_up_time = f"{time.time() - network_up_time:.3f}"
        self.server_time = time.time()

    def end_timing(self, *args, **kwargs ) -> dict:
        """
        Updates the response data with timing information and other server statistics.
        
        Args:
            payload: The original response data to be updated.
            self.network_up_time: The calculated network up time.
            server_time: The total time the server took to process the request.
        
        Returns:
            Updated response data with additional metadata.
        """
        time.sleep(0.01)
        return {
                            'network_up_time': self.network_up_time,
                            'server_time': f"{time.time() - self.server_time:.3f}",
                            'network_down_time': f"{time.time():.3f}",
        }

    def send_server_response(self, payload: dict, *args, status_code: int = 200, **kwargs):
        """
        Sends a JSON response with the specified status code.
        
        Args:
            payload: A dictionary to be sent as JSON.
            status_code: HTTP status code (default is 200).
        """
        try:
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        except Exception as e:
            print(f"Error sending response: {e}")
            self.send_error(500, str(e), *args, **kwargs)


class ServiceHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RequestHandlerClass.service = Endpoints(*args, **kwargs)


def run(server_class=ServiceHTTPServer, handler_class=SimpleHTTPRequestHandler, port=None, 
            *args, **kwargs
    ):
    server_address = ('', port if port is not None else msts.config.defaults.get('port'))
    httpd = server_class(server_address, handler_class, *args, **kwargs)
    print(f"Starting the HTTP server on port {port}...")
    httpd.serve_forever(*args, **kwargs)


if __name__ == '__main__':
    run()
