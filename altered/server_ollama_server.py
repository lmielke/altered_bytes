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
        print(f"{Fore.BLUE}Executing Ollama call with function: {func = }, \n\t{prompt = }, \n\t{params = }{Fore.RESET}")
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
            print(f"{Fore.RED}Calling Ollama server with function: {func = }, \n\t{params = }{Fore.RESET}")
            response_data = getattr(self.client, func)(prompt=prompt, **params)
            response.update(response_data)
            print(f"{Fore.GREEN}Ollama server response: {response}{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}Error executing Ollama call: {e}{Fore.RESET}")
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
