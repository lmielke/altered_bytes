import os, re, yaml
from jinja2 import Environment, FileSystemLoader
from colorama import Fore, Style
import altered.hlp_printing as hlpp
import altered.settings as sts

class Render:
    fields = ['prompt_title', 'context', 'user_prompt', 'instruct']

    def __init__(self, *args, **kwargs):
        self.templates_dir = sts.templates_dir
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
        self.context = self._load_context(*args, **kwargs)
        self.document = None

    def _load_context(self, *args, context_path:str=None, **kwargs):
        context_path = context_path if context_path else os.path.join(self.templates_dir, 'context.yml')
        try:
            with open(os.path.join(context_path), 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError as e:
            return {}

    def render(self, *args, template_name: str, context: dict=None, verbose:int=0, **kwargs):
        print(f"{verbose = }")
        template = self.env.get_template(template_name)
        context = context if context else self.context
        if verbose >= 2: hlpp.dict_to_table('Render.render.context', context)
        # we sort the keys to make sure the fields are in the correct order
        self.document = template.render({k: context.get(k) for k in self.fields})
        self.document = self.correct_ansi_codes(self.document, *args, **kwargs)
        return self.document

    def correct_ansi_codes(self, text, *args, **kwargs):
        # Replace escaped newlines with actual newlines
        text = text.replace('\\n', '\n')
        
        # Replace escaped ANSI codes with actual ANSI codes
        ansi_escapes = re.compile(r'\\033\[((?:\d+;)*\d+)?([a-zA-Z])')
        text = ansi_escapes.sub(lambda m: f'\033[{m.group(1) or ""}{m.group(2)}', text)
        
        return text

    def save_rendered(self, *args, template_name:str, output_file:str=None, **kwargs):
        output_file = output_file if output_file else sts.time_stamp()
        if not self.document:
            self.render(template_name=template_name)
        with open(os.path.join(self.templates_dir, 'temp', output_file), 'w') as file:
            file.write(self.document)