import json, os, re, yaml
from colorama import Fore, Style
import altered.hlp_printing as hlpp

class YmlParser:
    meta_flag = '# meta:'
    
    def __init__(self, *args, **kwargs):
        self._meta = {}
        self.data = {}

    def __call__(self, *args, **kwargs):
        return self.describe(*args, **kwargs)

    def add_labels(self, *args, name=None, labels=None, description=None, **kwargs):
        if labels:
            with open(labels, 'r') as file:
                self.fields = file.read()
                self._meta, fields = self.parse_content(*args, **kwargs)
                self.data = yaml.safe_load(self.fields)

        self._meta = dict(**{'fields_name': name, 'df_description': description}, **self._meta)

    def parse_content(self, *args, **kwargs):
        meta, fields = {}, {}
        for i, block in enumerate(self.fields.split('\n\n')):
            block = block.strip()
            if not block: continue
            if not block.startswith(self.meta_flag):
                if i != 0:
                    print(
                            f"\n{Fore.YELLOW}"
                            f"Warning: Missing meta flag in block {i}{Fore.RESET}\n"
                            f"{block}\n\n"
                            )
                continue
            _descriptions = []
            for line in block.split('\n'):
                if line.startswith(self.meta_flag):
                    m = json.loads(line.replace(self.meta_flag, '').strip())
                    meta[m['name']] = m
                elif line.startswith('#'):
                    _descriptions.append(line.replace('#', '').strip())
                else:
                    f = yaml.safe_load(line)
                    fields.update(f)
                    meta[m['name']]['description'] = '\n'.join(_descriptions)
                    meta[m['name']]['value'] = f[m['name']]
        return meta, fields

    def describe(self, *args, fmt='tbl', **kwargs):
        if fmt == 'tbl':
            return self._field_info_tabular()
        elif fmt in ['yaml', 'yml']:
            return self.fields[1:]
        elif fmt == 'json':
            return self._field_info_json()
        else:
            raise ValueError("Unsupported format. Use 'tbl', 'yaml', or 'dict'.")

    def _field_info_tabular(self, *args, **kwargs):
        hlpp.dict_to_table(self._meta['fields_name'], self._meta, *args, **kwargs)

    def _field_info_json(self, *args, **kwargs):
        """
        This returns not a real json string but a json like file with comments
        """
        json_str = ''
        for line in self.fields.split('\n')[1:]:
            if not line:
                json_str += '\n'
            elif not line.startswith('#') and ':' in line:
                k, vs = line.split(':', 1)
                j = '{' + f'"{k}": "{self._meta[k].get("example", "null")}"' + '},\n'
                j = re.sub(r'(")(\d+)(")', r'\2', j)
                j = j.replace('"null"', 'null').replace('""', 'null')
                j = j.replace('.yml', f'.json').replace('.yaml', f'.json')
                json_str += j
            else:
                json_str += f"{line}\n"
        return json_str
        