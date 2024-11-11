"""
server_ollama_server.py
Calls the Ollama server with timeout handling. Retries in case of a timeout.
"""

import subprocess
import threading
import time
from ollama import Client
from colorama import Fore, Style

import altered.model_params as msts
import altered.settings as sts


class OllamaCall:

    timeout: int = msts.config.params.get('timeout') # ollama server hangup timeout
    max_retries: int = msts.config.params.get('max_retries') # retries after hangup
    prc_name = 'ollama_llama_server.exe'

    def __init__(self, *args, **kwargs):
        """
        Initializes the OllamaCall class with the Ollama client.
        """
        self.client = Client(host=msts.config.params.get('ollama_host'))

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
        attempts = 1
        while attempts <= self.max_retries:
            thread = threading.Thread(
                target=self._call_ollama_server, 
                args=(func, prompt, params, response)
            )
            thread.start()
            thread.join(timeout=self.timeout)
            if thread.is_alive():
                print(
                        f"{Fore.YELLOW}Ollama server is unresponsive. "
                        f"Executing timeout handling...{Fore.RESET}"
                )
                self.execute_timeout()
                attempts += 1
                print(f"{Fore.YELLOW}Retrying {attempts}/{self.max_retries}{Fore.RESET}")
            else:
                break
        if attempts > self.max_retries:
            response['error'] = (
                f"Request timed out after {self.timeout * self.max_retries} seconds"
            )
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
        kill_cmd, process_id = self.get_kill_cmd()
        if kill_cmd:
            self.run_kill_cmd(kill_cmd, process_id)

    def get_kill_cmd(self) -> tuple:
        """
        Generates the command to kill the Ollama process running on the GPU.

        Returns:
            A tuple containing the kill command and the process ID.
        """
        try:
            process = subprocess.check_output(
                [
                    'powershell', '-Command',
                    (
                        f"Get-Process | Where-Object {{ $_.Path -like '*{self.prc_name}' }} "
                        f"| Select-Object -First 1 -ExpandProperty Id"
                    )
                ],
                text=True
            ).strip()
            if process:
                return f"taskkill /PID {process} /F", process
            else:
                print(
                    f"{Fore.RED}No process named {self.prc_name} was found." 
                    f"{Fore.RESET}"
                )
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error retrieving process ID: {e}{Fore.RESET}")
        return "", None

    def run_kill_cmd(self, kill_cmd: str, process_id: str = None):
        """
        Executes the provided kill command.

        Args:
            kill_cmd: The command to execute to kill the process.
            process_id: The ID of the process being killed.
        """
        if kill_cmd:
            try:
                subprocess.run(kill_cmd, shell=True, check=True)
                if process_id:
                    print(
                            f"{Fore.GREEN}Successfully killed process with ID {process_id}: "
                            f"{kill_cmd}{Fore.RESET}"
                    )
                else:
                    print(f"{Fore.GREEN}Successfully executed:{Fore.RESET} {kill_cmd = }")
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}Failed to execute kill command: {e}{Fore.RESET}")
