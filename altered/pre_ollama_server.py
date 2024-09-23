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


class Endpoints:

    def __init__(self, *args, **kwargs):
        self.ep_mappings = {
                                'get_generates': 'generate', 
                                'get_embeddings': 'embeddings', 
                            }
        self.ollama_params = {'prompt', 'options', 'keep_alive', 'stream', 'model'}
        self.prompt_counter = defaultdict(int)
        self.olc = Client(host='http://localhost:11434')
        # used for aggregations of responses
        self.instructs = Instructions(*args, **kwargs)
        self.renderer = Render(*args, **kwargs)

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

    def get_generates(self, ep:str, *args, prompts:list, repeats:int=1, **kwargs) -> dict:
        responses = []
        prompts = self.create_repeats(prompts, repeats, *args, **kwargs)
        for prompt in prompts:
            responses.append(self._ollama(self.ep_mappings.get(ep), prompt, *args, **kwargs))
        responses.extend(self.agg_resps(ep, *args, prompts=prompts, responses=responses,
                                             **kwargs,)['responses'])
        return {'responses': responses}

    def create_repeats(self, prompts:str, repeats:int=1, *args, **kwargs) -> list:
        if len(prompts) == 1 and repeats != 1:
            return [prompts[0] for _ in range(repeats)]
        else:
            return prompts

    def agg_resps(self, ep, *args, prompts:list, responses:list,
                                                        strat_templates:str=None, 
                                                        **kwargs, ):
        """
        Aggregates muliple responses into a single response using the provided 
        aggregation strategy. Also a std is estimated.
        """
        aggs = []
        if len(responses) >= 2 and strat_templates is not None:
            if not 'agg_std' in strat_templates: strat_templates.append('agg_std')
            for strat in strat_templates:
                print(f"{Fore.CYAN}{strat}{Style.RESET_ALL}")
                strats = self.instructs(    *args,
                                            strat_templates=[strat],
                                            prompts=prompts,
                                            responses=responses,
                                            **kwargs,
                                        )
                rendered = self.renderer.render(
                                            template_name='instructs.md',
                                            context = {'instructs': strats},
                                            verbose=3,
                                            )
                agg = self._ollama(self.ep_mappings.get(ep), rendered, *args, **kwargs)
                agg = {'rendered': rendered}
                agg['strat_templates'] = strat_templates
                agg['fmt'] = kwargs.get('fmt')
                aggs.append(agg)
        return {'responses': aggs}

    def unittest(self, *args, **kwargs) -> dict:
        """
        Generates the JSON response for the /unittest request.
        """
        response = self.ping(*args, **kwargs)
        # print(f"unittest: {kwargs = }")
        # response['agg_test'] = self.agg_resps(*args, **kwargs)
        return {'responses': [response]}

    def _ollama(self, func:str, prompt:str, *args, **kwargs) -> dict:
        """
        Generates the JSON response for the /_ollama request.
        """
        # Increment the /_ollama counter directly
        params = {k: vs for k, vs in kwargs.items() if k in self.ollama_params}
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
        self.start_timing(*args, **kwargs)
        ep, payload = self.get_endpoint(*args, **kwargs)
        # Route the request to the appropriate service ep
        print(f"do_POST: {ep, payload = }")
        payload.update(getattr(self.service, ep)(ep, *args, server=self.server, **kwargs))
        # Update response with timing information and other server statistics
        payload.update(self.end_timing(ep, *args, **kwargs))
        # Send the JSON response
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
        return ep, {'prompt_counter': self.service.prompt_counter}

    def start_timing(self, *args, network_up_time: float, **kwargs ) -> tuple:
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
        self.network_up_time = time.time() - network_up_time
        self.server_time = time.time()

    def end_timing(self, ep, *args, **kwargs ) -> dict:
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
        print(
                    f"\nService {ep} responded successfully. "
                    f"\n\tprompt_counter = {self.service.prompt_counter}, "
                    f"\n\ttotal_server_time = {time.time() - self.server_time:.2f}"
                    )
        return {
                            'network_up_time': self.network_up_time,
                            'server_time': time.time() - self.server_time,
                            'network_down_time': time.time(),
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
    print(f"{msts.config.defaults['port'] = }")
    port = port if port is not None else msts.config.defaults['port']
    server_address = ('', port)
    print(f"{server_address = }")
    httpd = server_class(server_address, handler_class)
    print(f"Starting the HTTP server on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
