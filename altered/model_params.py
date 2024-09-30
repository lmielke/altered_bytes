"""
model_settings.py
path: ~/python_venvs/libs/altered_bytes/altered/model_settings.py
This file contains the settings for the openAI model. 
Import: import altered.model_params as msts
msts.params.config, msts.params.api_key
"""

import os, re, requests, shutil
import yaml
from datetime import datetime as dt
from typing import Dict, Tuple, Union
import altered.settings as sts
from colorama import Fore, Style


class ModelParams:


    def __init__(self, *args, **kwargs):
        self.config = self._load_model_configs(*args, **kwargs)
        self.aliasses = self.config.get('aliasses', {})
        self.servers = self.config.get('servers', {})
        self.models = self.config.get('models', {})
        self.defaults = self.config.get('defaults', {})
        self.last_update = dt.now().strftime('%Y-%m-%d')
        self.api_key = self.get_api_key(*args, **kwargs)
        self.services = self.get_services(*args, **kwargs)
        self.update_models_infos(*args, **kwargs)

    def get_config_path(self, *args, **kwargs) -> str:
        try:
            config_path = sts.models_config_path
            if not os.path.isfile(config_path):
                raise AttributeError
        except AttributeError:
            config_path = self.mk_config_path(*args, **kwargs)
            exit()
        return config_path

    def mk_config_path(self, *args, **kwargs):
        while True:
            msg =   (   f"You have not yet specified a config directory for your "
                        f"models_servers.yml file. "
                        f"{Fore.YELLOW}Specify a config directory: {Fore.RESET}"
                    )
            config_dir = input(msg).strip()
            if os.path.isdir(config_dir):
                break
            else:
                print(f"{Fore.RED}Invalid directory:{Fore.RESET} {config_dir}")
        model_config_path = os.path.join(   os.path.abspath(config_dir),
                                            os.path.basename(sts.default_config_path)
                            )
        longest, model_config_path = [], os.path.abspath(model_config_path)
        # the user may specify the default_config_path in which case nothing is copied
        if os.path.abspath(sts.default_config_path) != model_config_path:
            shutil.copyfile(sts.default_config_path, model_config_path)
        # we try to shorten model_config_path by using existing paths in settings.py
        for k, vs in sts.__dict__.items():
            if vs and type(vs) == str:
                if os.path.isdir(vs):
                    vs = os.path.abspath(vs)
                    if len(vs) <= 100 and vs in model_config_path:
                        if not longest or len(longest[0]) < len(vs):
                            longest = [vs, k]
        if longest:
            model_config_path = os.path.relpath(model_config_path, longest[0])
            model_config_str = (
                                    f"os.path.join("
                                    f"{longest[1]}, "
                                    f"'{model_config_path}')"
                                )
        else:
            model_config_str = f"'{model_config_path}'"

        # append config_path to settings.py file
        with open(sts.__file__, 'a') as s:
            s.write(f"\n\nmodels_config_path = {model_config_str.replace(os.sep, '/')}")
        print(  f"{Fore.GREEN}File {model_config_str} has been created.{Fore.RESET} "
                f"Open and adjust as you require! \n"
                f"{Fore.YELLOW}Then run this command again!{Fore.RESET}"
                )
        return model_config_path

    def _load_model_configs(self, *args, **kwargs) -> Dict:
        path = self.get_config_path(*args, **kwargs)
        with open(path, 'r') as file:
            return yaml.safe_load(file)

    def _write_model_configs(self, *args, **kwargs):
        path = self.get_config_path(*args, **kwargs)
        with open(path, 'w') as file:
            yaml.safe_dump(self.config, file)

    def unpack_alias(self, *args, alias:str=None, service_endpoint:str=None, **kwargs) -> Tuple[str, str]:
        """
        alias:[str, tuple] combined model_server alias 
                            i.e. 'l31:8b_0' -> (modelAlias_server_id)
                            i.e. (llama3.1, while_ai_0) -> (ollama model, hostname)
            An alias consists of 
                1. a model alias and 
                2. a server alias connected by a underscore '_'.
            NOTE: see os.dirname(__file__)./resources/models/models_servers.yml
            The model alias is used to find the model name in the aliasses dictionary.
            Example: Server name is while_ai_0 (0) and while_ai_1 (1) and model name 
                    is llama3.1 (l31)
                    Then the combined alias for model/server would be l31:8b_0 and l31:8b_1.
        """
        # gpt´s can be delivered with any server_alias, it will always be oai
        # if alias is None and service_endpoint is None:
        #     raise ValueError(f"{Fore.RED}Alias or service_endpoint must be specified{Fore.RESET}")
        model_name, server_name = None, None
        if (alias is None) and (service_endpoint is None):
            service_endpoint = self.defaults.get('service_endpoint')
        if alias is None:
            model_alias, server_alias = None, None
            model_name = self.defaults.get(service_endpoint)['model']
            server_name = self.defaults.get(service_endpoint)['server']
            # server_name = self.defaults['servers'].get(service_endpoint)
            return model_name, server_name
        elif type(alias) == tuple:
            model_alias, server_alias = None, None
            model_name, server_name = alias
            return model_name, server_name
        elif alias.startswith('gpt'):
            if '_' in alias:
                model_alias, _ = alias.split('_')
            else:
                model_alias = alias
            server_alias = 'oai'
        elif '_' in alias:
            model_alias, server_alias = alias.split('_')
        else:
            model_alias, server_alias = alias, None
        # replace this for something more general
        model_name = self.aliasses['models'].get(model_alias, {})
        server_name = self.aliasses['servers'].get(server_alias, {})
        if not server_name: server_name = self.defaults.get('get_embeddings', {})['server']
        if model_name:
            return model_name, server_name
        else:
            raise ValueError(f"Alias '{alias}' not found in the aliasses dictionary")

    def update_servers(self, server_name: str, params: Dict[str, Union[str, int, None]], *args, **kwargs):
        if server_name in self.servers:
            self.servers[server_name].update(params)
            self.last_update = dt.now().strftime('%Y-%m-%d')
        else:
            raise ValueError(f"Server '{server_name}' not found in servers")

    def get_model(self, *args, **kwargs) -> dict:
        """
        Takes an model alias and returns the model parameters like server_name and 
        server params.
        """
        model_name, server_name = self.unpack_alias(*args, **kwargs)
        model_file = self.models.get(model_name)
        if server_name == 'openAI' or server_name is None:
            api_key = self.get_api_key()
            params = {'api_key': api_key,}
        elif server_name is not None:
            params = self.servers.get(server_name)
            if params is None:
                raise ValueError(f"Parameters for server '{server_name}' not found")
        return {'model_file': model_file, 'server': server_name, 'params': params, }

    def get_url(self, *args, service_endpoint:str=None, **kwargs) -> str:
        """
        Retrieves the URL for the specified model alias.
        alias:str combined model_server alias i.e. 'l31:8b_0' or 'l31:8b_1'.
        service_endpoint:str ['get_embeddings', 'generate']

        Returns:
            str: The URL for the model alias.
        """
        sp = self.get_model(*args, service_endpoint=service_endpoint, **kwargs).get('params')
        port = sp.get(f'{service_endpoint}_port', '')
        url = f"{sp.get('model_address', '')}:{port}/api/{service_endpoint}"
        return url

    def get_api_key(self, *args, **kwargs) -> str:
        """
        Retrieves the API key from the specified key path.
        
        Returns:
            str: The API key value or None if the key could not be retrieved.
        """
        # Retrieve the key_path for openAI
        key_path = self.servers.get('openAI', {}).get('key_path')
        assert key_path, "Key path not found in servers"
        # Unpack path alias (assuming this function resolves any path aliases)
        key_path = self.unpack_path_alias(key_path, *args, **kwargs)
        try:
            # Attempt to open and load the YAML file
            with open(key_path, 'r') as file:
                s_file = yaml.safe_load(file)
                self.api_key = s_file.get('key')
                if not self.api_key:
                    print("API key not found in the YAML file.")
        except FileNotFoundError:
            print(f"File not found: {key_path}")
            self.api_key = None
        except OSError as e:
            print(f"OSError occurred while trying to read the file: {e}")
            self.api_key = None
        except yaml.YAMLError as e:
            print(f"Error loading YAML file: {e}")
            self.api_key = None
        # Return the API key or None if it was not found or an error occurred
        return self.api_key

    def unpack_path_alias(self, key_path:str, *args, **kwargs):
        # key_path may start with a reference to an environment variable
        key_path_elements = key_path.split('/')
        match = re.search(r"os\.environ\.get\('([A-Za-z0-9_]*)'\)", key_path_elements[0])
        if match:
            key_path_elements[0] = os.environ.get(match.group(1))
            key_path = os.path.join(*key_path_elements)
            key_path = os.path.expanduser(key_path)
            key_path = os.path.abspath(key_path)
        if not isinstance(key_path, str):
            raise ValueError("key_path must be a string")
        if not os.path.isfile(key_path):
            print(f"File not found: {key_path}! {Fore.RED}Unable to connect to openAi.{Fore.RESET}")
        if not (key_path.endswith('.yml') or key_path.endswith('.yaml')):
            raise ValueError("The key file must be a YAML file")
        # expanduser
        return key_path

    def get_services(self, *args, **kwargs) -> Dict:
        """
        Retrieves the services from the model configuration file.

        Returns:
            Dict: A dictionary containing the service endpoints.
        """
        services = self.config.get('services', {})
        # some services use parameter files (.yml) for keys in which case they have a key_path
        # we find those key_path s and replace key_path by the content of the key file.
        for service, params in services.items():
            if 'key_path' in params.keys():
                key_path = self.unpack_path_alias(params['key_path'])
                services[service].update(self.load_service(key_path, *args, **kwargs))
        return services

    def load_service(self, file_path: str, *args, **kwargs) -> dict:
        """
        Load a service file from a specified path.

        Args:
            file_path (str): The path to the service file.

        Returns:
            dict: The service file as a dictionary.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Key file not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = yaml.safe_load(file)
            print(f"Service file loaded: {content}")
        return content

    def get_model_file(self, url, *args, **kwargs) -> tuple:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(    f"Failed to retrieve content from URL. "
                                f"Status code: {response.status_code}"
                    )
        update_time = ' '.join(
                                re.search(r'(Updated)\s(\d+)\s(\w*\sago)', 
                                response.text).group(2, 3)
                                )
        return response.text, update_time


    def extract_model_info(self, alias, url: str, *args, **kwargs) -> dict:
        """
        Extract model information from the HTML content of a specific URL.

        Args:
            url (str): The URL to the specific blob.

        Returns:
            dict: A dictionary containing the model name, architecture, file type,
                  context length, and embedding length.
        """
        search_terms = ['general.architecture', 'general.file_type', 'context_length', 
                        'embedding_length', ]
        r_text, update_time = self.get_model_file(url, *args, **kwargs)
        prev_update_time = self.get_model(alias).get('model_file').get('last_update')
        rs = {
                'last_update': update_time, 
                'new_update_available': (   self.string_to_days(update_time) <
                                            self.string_to_days(prev_update_time)
                                        ),
                }
        for r in r_text.split('</li>'):
            for term in search_terms:
                if term in r:
                    rs[term] = r.split(term)[-1].strip().strip('</div>').strip().split()[-1]
        for term in search_terms:
            if term not in rs:
                rs[term] = None
        return rs

    def string_to_days(self, age_string, *args, **kwargs) -> int:
        ages = {'days': 1, 'weeks': 7, 'months': 30}
        age_string = age_string.split()
        if len(age_string) != 3:
            raise ValueError(f"Invalid age string: {age_string}")
        if not age_string[0].isnumeric():
            raise ValueError(f"First element of age string {age_string[0]} must be a number")
        if age_string[1] not in ages:
            raise ValueError(f"Invalid unit in age string: {age_string[2]}")
        num, unit = int(age_string[0]), age_string[1]
        return num * ages.get(unit)
        
    def update_models_infos(self, *args, yes:bool=False, **kwargs):
        if not yes: return False
        url_parts = ["https://ollama.com/library", "blobs"]
        ignores, strips = ['openAI', 'gpt'], ['-256k']
        models = self.config.get('aliasses', {}).get('models', {})
        for alias, model_file in models.items():
            name, blob = model_file['name'], model_file['blob_id']
            _name = name
            for st in strips:
                _name = _name.strip(st)
            if not any([ignore in _name for ignore in ignores]):
                print(f"{Fore.YELLOW}Updating model_file info for:{Fore.RESET} {name}")
                try:
                    url = '/'.join([url_parts[0], _name, url_parts[1], blob])
                    params = self.extract_model_info(alias, url)
                    self.config['aliasses']['models'][alias].update(params)
                except Exception as e:
                    print(f"{Fore.RED}Failed to extract model{Fore.RESET} params for '{name}': {e}")
        self._write_model_configs()

class SingleModelParams(ModelParams):
    """
    SingleModelParams is a singleton subclass of ModelParams that ensures only one instance 
    of the model configuration parameters is created. 
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingleModelParams, cls).__new__(cls)
        return cls._instance


config = SingleModelParams()
