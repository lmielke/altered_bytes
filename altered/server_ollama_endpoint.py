import json, os, time, yaml
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from colorama import Fore, Style
from ollama import Client
import random as rd
import socket

from altered.server_ollama_server import OllamaCall
import altered.model_params as msts
import altered.settings as sts


class Endpoints:

    def __init__(self, *args, **kwargs):
        """
        Initializes the Endpoints class, sets up the Ollama call instance, and prepares endpoint mappings.
        """
        self.ep_mapps = {
            'get_generates': 'generate',
            'get_embeddings': 'embeddings',
        }
        # Used to filter the kwargs for the ollama client
        self.ollama_params = {'prompt', 'options', 'keep_alive', 'stream', 'model'}
        self.ollama_formats = {'json', }
        self.api_counter = defaultdict(int)
        self.ollama_call = OllamaCall(*args, **kwargs)

    def get_embeddings(self, ep, *args, prompts: list, **kwargs) -> dict:
        """
        Retrieves embeddings for the provided prompts.

        Args:
            ep (str): The endpoint name.
            prompts (list): List of prompts to send to the Ollama server.

        Returns:
            dict: The server's responses containing embeddings.
        """
        responses = []
        for prompt in prompts:
            params = {k: v for k, v in kwargs.items() if k in self.ollama_params}
            responses.append(self.ollama_call.execute(self.ep_mapps.get(ep), prompt, params))
            self.prompt_counter[ep] += 1
        return {'responses': responses}

    def get_generates(self, ep: str, *args, prompts: list, repeats: int = sts.repeats, **kwargs) -> dict:
        """
        Generates text for the provided prompts, repeating as specified.

        Args:
            ep (str): The endpoint name.
            prompts (list): List of prompts to send to the Ollama server.
            repeats (int): Number of times to repeat generation for each prompt.

        Returns:
            dict: The server's responses containing generated texts.
        """
        responses = []
        for i, prompt in enumerate(prompts):
            for repeat in range(repeats['num']):
                params = {k: v for k, v in kwargs.items() if k in self.ollama_params}
                responses.append(self.ollama_call.execute(self.ep_mapps.get(ep), prompt, params))
                self.prompt_counter[ep] += 1
        return {'responses': responses}


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    service = None  # This will be set when the server starts
    allowed_endpoints = {'get_generates', 'get_embeddings'}

    def do_GET(self, *args, **kwargs):
        """
        Handles the GET requests. Specifically checks for /ping endpoint and returns
        server start time and uptime.
        """
        if self.path == '/ping':
            payload = {
                'status': f"running since: {self.server.server_start_time}",
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        else:
            self.send_error(404, f"Not a valid endpoint: '{self.path}'")


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
            self.service.api_counter[ep] += 1
            self.service.prompt_counter = defaultdict(int)
        return ep, {
                    'api_counter': self.service.api_counter, 
                    'prompt_counter': self.service.prompt_counter
                    }

    def start_timing(self, *args, network_up_time: float=None, **kwargs ) -> tuple:
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
        if network_up_time is None:
            print(f"{Fore.YELLOW}Warning: No network_up_time passed from client!{Fore.RESET}")
            network_up_time = time.time()
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
        time.sleep(0.001)
        return {
                            'network_up_time': (self.network_up_time),
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
    httpd.server_start_time = sts.run_time_start
    print(f"Starting the HTTP server at {httpd.server_start_time}, on port {port}...")
    print(f"ping me like: curl http://{socket.gethostbyname(socket.gethostname())}:{port}/ping")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
