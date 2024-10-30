"""
yml_parser.py
This module manages fields for the application data base (i.e. class Data).
In Data it is used to define the column structure of the underlying DataFrame. 
Also YmlParser is used to generate text versions of underlying fields for
use in prompt generation.

YmlParser produces 3 critical outputs:
self.data: a dictionary of the fields and their default values
- contains a single data record
- can be populated as a dictionary and be added to the DataFrame
- be used to render a data record to a prompt
- example: 
    {'name': 'color_of_sky', 'prompt': 'why is the sky blue', 'category': 'physics', ...}

self.fields: a dictionary of the fields and their meta data
- contains the field definition for every field in self.data
- can be used to create the DataFrame with appropriate columns and data types
- can be used for field validations and mappings
- example:
    {'name': 'category', 'dtype': 'categorical', 'example': 'physics', 'mappings': None}

self.fields_text: a string representation of the fields in various formats (json, yml, markdown)
- contains a comprehensive text representation of the fields
- mainly used for documentation and prompt generation
- extensive comments are used to describe the fields to users and the LLM
- example:
    # meta: {"name": "prompt", "type": "string", "default": "", "example": "Hello, Who are you?"}
    # prompt contains the prompt/problem statement that founds/initiates the thought/chat
    prompt: {{ prompt }}

    # meta: {"name": "response", "type": "string", "default": "", "example": "I am a helpful assistant. How can I help you today?"}
    # The response field contains the model response
    response: {{ response }}

"""


import json, os, re, yaml
from enum import Enum
from colorama import Fore, Style
import altered.hlp_printing as hlpp


class Format(Enum):
    JSON = 'json'
    YAML = 'yaml'
    YML = 'yml'
    MARKDOWN = 'markdown'


class YmlParser:
    file_meta_flag = '# file_meta:'
    meta_flag = '# meta:'
    replaces = {r'\{{': r'{{',}
    code_regex = r'^([a-zA-Z_0-9]*)(?:\s*:\s*(.*)$)'
    code_multi_line = r'(^[a-zA-Z_0-9]*)(?:\s*:\s*>$)'
    
    def __init__(self, *args, **kwargs):
        self.fields = {}
        self.data = {}
        self.fields_text = ''
        self.fields_name = ''
        self.fields_example = ''
        self(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.load_fields(*args, **kwargs)
        return self.add_labels(*args, **kwargs)

    def load_fields(self, *args, fields_paths:list, **kwargs):
        self.fields_name = os.path.basename(fields_paths[0]).split('.')[0]
        for path in fields_paths:
            with open(path, 'r') as f:
                # we remove the first line from the file as it is the fields file name
                file = f.read()
                blocks = file.split('\n\n')
                self.fields_text += ('\n\n'.join(blocks[1:]) + '\n' ).replace('\n'*3, '\n'*2)
        match = re.search(fr"({self.file_meta_flag})(.*)$", blocks[0])
        if match:
            self.fields_example = json.loads(match.group(2))


    def add_labels(self, *args, description=None, **kwargs):
        self.fields = self.parse_meta(*args, **kwargs)
        self.data = yaml.safe_load(self.fields_text)
        self.fields.update({'fields_name': self.fields_name,
                            'df_description': ' '.join(
                                                    re.findall(r'(?:^# Description:\s)(.*)', 
                                                    self.fields_text, re.M)
                                                    ), 
                                }, )
        self.fields_text = self.cleanup_fields_text(*args, **kwargs)
        return self.fields

    def cleanup_fields_text(self, *args, **kwargs):
        """
        self.fields_text is a concatenation of fields files. In some cases the fields files
        might contain identical fields, resulting in redundant fields. This method removes 
        the redundant fields.
        """
        
        fields_text, fields = '', set()
        for i, block in enumerate(self.fields_text.split(self.meta_flag)):
            if not block: continue
            block = self.meta_flag + block
            for fr, to in self.replaces.items():
                block = block.replace(fr, to)
            for line in block.strip().split('\n'):
                match = re.match(self.code_regex, line)
                if match:
                    field_name = match.group(1)
                    break
                else:
                    field_name = None
            if field_name is None:
                fields_text += block
            if field_name and not (field_name in fields):
                fields.add(field_name)
                fields_text += block
        msg = (
                f"{Fore.RED}yml_parser.cleanup_fields_text,  "
                f"missing or redundant field during cleanup! "
                f"Check .yml files formats for missing linebreaks ect. {Fore.RESET}: "
                f"{fields - self.data.keys()}"
                f"{fields} - {self.data.keys()}"
                )
        assert not (fields - self.data.keys()), msg
        return fields_text

    def parse_meta(self, *args, **kwargs):
        meta = {}
        for i, block in enumerate(self.fields_text.split(self.meta_flag)):
            if not block: continue
            block = (self.meta_flag + block).strip()
            if not block: continue
            if not block.startswith(self.meta_flag):
                if i != 0:
                    print(
                            f"\n{Fore.YELLOW}"
                            f"Warning: Missing meta flag in block {i}{Fore.RESET}\n"
                            f"{block}\n\n"
                            )
                continue
            _descriptions, code_block = [], []
            block = block.strip() + '\n'
            for line in block.split('\n'):
                if line.startswith(self.meta_flag):
                    m = json.loads(line.replace(self.meta_flag, '').strip())
                    meta[m['name']] = m
                    continue
                elif line.startswith('#'):
                    _descriptions.append(line.replace('#', '').strip())
                    continue
                elif re.match(self.code_multi_line, line.strip()) or code_block and line != '':
                    # yaml entries can be multiline like: fieldname: >\nto be continued 
                    # with additional lines ...
                    # multiline must be properly parsed
                    code_block.append(line)
                    continue
                elif re.match(self.code_regex, line):
                    f = yaml.safe_load(line)
                elif line == '' and code_block:
                    f = yaml.safe_load('\n'.join(code_block))
                    code_block = []
                meta[m['name']]['description'] = '\n'.join(_descriptions)
                meta[m['name']]['value'] = f[m['name']]
        return {'meta': meta}

    def describe(self, *args, fmt='tbl', **kwargs):
        if fmt == 'tbl':
            return self._field_info_tabular()
        elif fmt in ['yaml', 'yml']:
            return self.fields_text[1:]
        elif fmt == 'json':
            return self._field_info_json()
        elif fmt == 'markdown':
            return self._field_info_markdown()
        else:
            raise ValueError("Unsupported format. Use 'tbl', 'yaml', 'json', or 'markdown'.")

    def _field_info_tabular(self, *args, **kwargs):
        hlpp.dict_to_table(self.fields['fields_name'], self.fields, *args, **kwargs)

    def _field_info_json(self, *args, **kwargs):
        """
        This returns not a real json string but a json like file with comments
        """
        json_str, code_block = '', []
        for line in self.fields_text.split('\n')[1:]:
            if line.startswith(self.meta_flag): continue
            if not line:
                if code_block:
                    vs = '\n'.join(code_block[1:])
                    j = '{' + f'"{k}": "{self.fields["meta"][k].get("example", "null")}"' + '},\n'
                    j = re.sub(r'(")(\d+)(")', r'\2', j)
                    j = j.replace('"null"', 'null').replace('""', 'null')
                    j = j.replace('.yml', f'.json').replace('.yaml', f'.json')
                    json_str += j
                    json_str += '\n'
                    code_block = []
                else:
                    json_str += '\n'
                    continue
            elif re.match(self.code_multi_line, line.strip()) or code_block:
                if code_block:
                    code_block.append(line)
                else:
                    k = re.match(self.code_multi_line, line.strip()).group(1)
                    code_block.append(k)
                continue
            elif re.match(self.code_regex, line.strip()) or code_block:
                if code_block:
                    code_block.append(line)
                else:
                    k = re.match(self.code_regex, line.strip()).group(1)
                    code_block.append(k)
                continue                
            else:
                json_str += f"{line}\n"
                if code_block: code_block.append(line)
        return json_str
        
    def _field_info_markdown(self, *args, **kwargs) -> str:
        """
        Converts the JSON-like string with comments into Markdown format with comments.
        
        Comments are preserved as "md comment symbol" in the output.
        """
        json_str = self._field_info_json(*args, **kwargs)
        # Initialize Markdown string
        markdown_str = ""
        # Split the string into lines and process each line
        for line in json_str.splitlines():
            line = line.strip()
            # Process comments
            if line.startswith("#"):
                # Convert JSON-style comments to Markdown comments
                comment = re.sub(r'#', '> ', line)
                markdown_str += f"{comment}\n"
            elif line.startswith("{") and line.endswith("},"):
                # Convert JSON key-value pair into a Markdown format
                try:
                    # Convert JSON-like string to Python dictionary
                    json_obj = eval(line.strip(","))
                    for key, value in json_obj.items():
                        markdown_str += f"# {key.capitalize()}\n{value}\n\n"
                except:
                    pass  # Handle any malformed JSON-like strings
        return markdown_str.strip().replace('<lb>', '\n')

