import json, os, time, yaml
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from colorama import Fore, Style
from ollama import Client
import random as rd

from altered.server_ollama_server import OllamaCall
import altered.model_params as msts
import altered.settings as sts


import subprocess
import threading
import time
from ollama import Client
from colorama import Fore, Style


class OllamaCall:
    def __init__(self, host: str = 'http://localhost:11434', timeout: int = 30, *args, **kwargs):
        """
        Initializes the OllamaCall class with the Ollama client and timeout settings.

        Args:
            host (str): The host address of the Ollama server.
            timeout (int): Timeout in seconds for handling stuck requests.
        """
        self.client = Client(host=host)
        self.timeout = timeout
        self.ollama_process_name = 'ollama_llama_server.exe'

    def execute(self, func: str, prompt: str, params: dict) -> dict:
        """
        Executes the function call to the Ollama server with timeout handling.

        Args:
            func (str): The function to call on the Ollama client.
            prompt (str): The prompt to be sent to Ollama.
            params (dict): Additional parameters for the Ollama call.

        Returns:
            dict: The response from the Ollama server or an error response if timed out.
        """
        response = {}
        thread = threading.Thread(target=self._call_ollama_server, args=(func, prompt, params, response))
        thread.start()
        thread.join(timeout=self.timeout)

        if thread.is_alive():
            print(f"{Fore.YELLOW}Ollama server is unresponsive. Executing timeout handling...{Fore.RESET}")
            self.execute_timeout()
            response['error'] = f"Request timed out after {self.timeout} seconds"
        return response

    def _call_ollama_server(self, func: str, prompt: str, params: dict, response: dict):
        """
        Calls the specified function on the Ollama client.

        Args:
            func (str): The function to call on the Ollama client.
            prompt (str): The prompt to be sent to Ollama.
            params (dict): Additional parameters for the Ollama call.
            response (dict): A reference dictionary to store the server response.
        """
        try:
            response_data = getattr(self.client, func)(prompt=prompt, **params)
            response.update(response_data)
        except Exception as e:
            response['error'] = str(e)

    def execute_timeout(self):
        """
        Executes the timeout handling by running a kill command for the Ollama process.
        """
        kill_cmd = self.get_kill_cmd()
        self.run_kill_cmd(kill_cmd)

    def get_kill_cmd(self) -> str:
        """
        Generates the command to kill the Ollama process running on the GPU.

        Returns:
            A string representing the kill command for the Ollama process.
        """
        try:
            process = subprocess.check_output(
                [
                    'powershell', '-Command',
                    f"Get-Process | Where-Object {{ $_.Path -like '*{self.ollama_process_name}' }} | Select-Object -First 1 -ExpandProperty Id"
                ],
                text=True
            ).strip()
            if process:
                return f"taskkill /PID {process} /F"
            else:
                print(f"{Fore.RED}No process named {self.ollama_process_name} was found.{Fore.RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error retrieving process ID: {e}{Fore.RESET}")
        return ""

    def run_kill_cmd(self, kill_cmd: str):
        """
        Executes the provided kill command.

        Args:
            kill_cmd: The command to execute to kill the process.
        """
        if kill_cmd:
            try:
                subprocess.run(kill_cmd, shell=True, check=True)
                print(f"{Fore.GREEN}Successfully executed kill command: {kill_cmd}{Fore.RESET}")
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}Failed to execute kill command: {e}{Fore.RESET}")


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    service = None  # This will be set when the server starts
    allowed_endpoints = {'get_generates', 'get_embeddings'}

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
    print(f"Starting the HTTP server on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
