
import json
import time
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from ollama import Client
from collections import defaultdict
from colorama import Fore

class Endpoints:

    def __init__(self, *args, **kwargs):
        self.ep_mappings = {
            'get_generates': 'generate',
            'get_embeddings': 'embeddings',
        }
        self.ollama_params = {'prompt', 'options', 'keep_alive', 'stream', 'model'}
        self.ollama_formats = {'json'}
        self.api_counter = defaultdict(int)
        self.prompt_counter = defaultdict(int)
        self.olc = Client(host='http://localhost:11434')

    def ping(self, *args, server: object, **kwargs) -> dict:
        """
        Generates the JSON response for the /ping request.
        """
        return {
            'response': 'pong',
            'server_ip': server.server_address[0],
            'server_port': server.server_address[1]
        }

    def get_generates(self, ep: str, *args, prompt: str, **kwargs) -> dict:
        response = self._ollama_threaded(self.ep_mappings.get(ep), prompt, *args, **kwargs)
        self.prompt_counter[ep] += 1
        return {'response': response}

    def _ollama_threaded(self, func: str, prompt: str, *args, timeout: int = 10, **kwargs) -> dict:
        """
        Calls the Ollama client in a separate thread with a timeout.
        If the timeout is exceeded, a kill command is executed to stop the Ollama process.
        """
        result = {}

        def call_ollama():
            try:
                params = {k: v for k, v in kwargs.items() if k in self.ollama_params}
                response = getattr(self.olc, func)(prompt=prompt, **params)
                result['response'] = response
            except Exception as e:
                result['error'] = str(e)

        thread = threading.Thread(target=call_ollama)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.execute_timeout()
            result['error'] = 'Request timed out and process was killed'
        return result

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
                ['powershell', '-Command', "Get-Process | Where-Object { $_.Path -like '*ollama_llama_server.exe' } | Select-Object -First 1 -ExpandProperty Id"],
                text=True
            ).strip()
            if process:
                return f"taskkill /PID {process} /F"
            else:
                print(f"{Fore.RED}No process named ollama_llama_server.exe was found.{Fore.RESET}")
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
    service = None
    allowed_endpoints = {'ping', 'get_generates', 'get_embeddings'}

    def do_POST(self, *args, **kwargs):
        """
        Handles the POST requests by routing to the appropriate service method
        and sending the response as JSON. Tracks the prompt counter and timing information.
        """
        # Update kwargs with the parsed JSON body from the client
        kwargs.update(self.get_kwargs(*args, **kwargs))
        print(f"{Fore.RED}do_POST in:{Fore.RESET} {kwargs.get('verbose') = }")
        self.start_timing(*args, **kwargs)
        ep, payload = self.get_endpoint(*args, **kwargs)
        # Route the request to the appropriate service endpoint
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

    def start_timing(self, *args, network_up_time: float = None, **kwargs):
        """
        Explicitly handles network_up_time passed from kwargs.
        
        Args:
            network_up_time: The time when the network started, passed from the client.
        """
        self.network_up_time = time.time() - network_up_time if network_up_time else time.time()
        self.server_start_time = time.time()

    def end_timing(self, ep, *args, **kwargs) -> dict:
        """
        Updates the response data with timing information and other server statistics.
        
        Args:
            ep: The endpoint being processed.
        
        Returns:
            A dictionary with updated timing metadata.
        """
        processing_time = time.time() - self.server_start_time
        network_down_time = time.time()
        print(
            f"\nService {ep} responded successfully. "
            f"\n\tprompt_counter = {self.service.prompt_counter}, "
            f"\n\ttotal_server_time = {processing_time:.2f}"
        )
        return {
            'network_up_time': self.network_up_time,
            'server_processing_time': processing_time,
            'network_down_time': network_down_time,
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


def run(server_class=ServiceHTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000, *args, **kwargs):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting the HTTP server on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
