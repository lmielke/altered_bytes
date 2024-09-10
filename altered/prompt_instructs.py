"""
prompt.py

"""
import os, yaml
import altered.settings as sts
from colorama import Fore, Style

class Instructions:
    fmts = {'json', 'markdown', 'yaml'}

    def __init__(self, instructs:str=None, *args, **kwargs):
        self.instructs_fmts = self.load_prompt_params('prompt_formats', *args, **kwargs)
        self.instruction_params = self.load_prompt_params('prompt_intros', *args, **kwargs)
        self._data = instructs if instructs is not None else ''

    def __call__(self, *args, **kwargs):
        self.get_user_prompt(*args, **kwargs)
        self.create_instruct_dict(*args, **kwargs)
        self.set_response_format(*args, **kwargs)
        return self

    @property
    def user_prompt(self, *args, **kwargs):
        return self._user_prompt

    @property
    def data(self, *args, **kwargs):
        return self._data

    def get_user_prompt(self, *args, user_prompt:str=None, **kwargs):
        self._user_prompt = user_prompt

    def create_instruct_dict(self, *args, instructs:str='', **kwags):
        msg = (
                f"{Fore.RED}ERROR in Instructions.create_instruct_dict: "
                f"Provide either self._user_prompt or instructs! {Fore.RESET}"
                )
        assert self._user_prompt or instructs, msg
        # depending on the inputs the prompt is constructed with self._user_prompt and instructs
        if self._user_prompt and not instructs:
            # this should instruct the model to respond to the self._user_prompt directly
            instructs = self.instruction_params.get('msg_and_not_instructs_prefix', '')
        elif self._user_prompt and instructs:
            # in this case the self._user_prompt is only additional context to the prompt
            # the model should respond to the instructs and not the self._user_prompt
            prefix = self.instruction_params.get('msg_and_instructs_prefix', '')
            instructs = f"{prefix}\n\n{instructs}"
        self._data = {'Your Task': instructs}

    def set_response_format(self, *args, fmt:str=None, **kwargs):
        """
        Formats can be 'json', 'markdown', or 'yaml'.
        The corresponding strategy yaml file starts with the fmt name.
        """
        if not fmt:
            return
        elif fmt and (fmt not in self.fmts):
            raise ValueError(f"Error: Invalid fmt '{fmt}' provided.")
        # we add instructions for the response fmts to the prompt
        # Example: 'json_response_prefix' contains the instruct prefix if the fmt is 'json'
        # expected from the model (markdown, json, yaml)
        names = [f'{fmt}_response_{n}' for n in ['prefix', 'default_template', 'postfix',]]
        self._data['fmts'] = (f"{''.join([self.instructs_fmts[n] for n in names ] )}")

    def load_prompt_params(self, file_name, *args, **kwargs):
        params_path = os.path.join(sts.resources_dir, 'strategies', f"{file_name}.yml")
        with open(params_path, 'r') as f: 
            return yaml.safe_load(f)