import os
import re
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, Set, Tuple
from colorama import Fore, Style, Back
from jinja2 import Environment, FileSystemLoader, Template, nodes

import altered.settings as sts

template_path = os.path.join(sts.templates_dir, 'i_instructs_io.md')
tech_fields = {'io_meth', 'io_type', 'method'}

@dataclass
class IoFields:
    # technical fields
    io_meth: str
    io_type: str
    method: Dict[str, Any] = field(default_factory=dict)
    # dynamic fields
    fmt: str = 'markdown'
    fmt_comment: Optional[str] = None

    def __post_init__(self, *args, **kwargs):
        if not self.io_meth:
            raise ValueError(f"{Fore.RED}Key must not be empty{Fore.RESET}")
        if not self.io_type:
            raise ValueError(f"{Fore.RED}io_type must not be empty{Fore.RESET}")
        self.check_template(*args, **kwargs)

    def check_values(self, *args, **kwargs):
        expected_fields = set(self.__annotations__.keys())
        actual_fields = set(self.__dict__.keys())
        missing_fields = {field for field in expected_fields if getattr(self, field) is None}
        additional_fields = actual_fields - expected_fields
        if missing_fields - tech_fields:
            print(
                f"{Fore.YELLOW}IoFields VALUE WARNING:{Fore.RESET} "
                f"Missing Fields (None values): "
                f"{Fore.YELLOW}{', '.join(missing_fields)}{Fore.RESET}"
            )

        if additional_fields:
            print(
                f"{Fore.YELLOW}IoFields VALUE WARNING:{Fore.RESET} "
                f"Unexpected Fields: {Fore.YELLOW}{', '.join(additional_fields)}{Fore.RESET}"
            )

    def load_and_extract_vars(self, *args, **kwargs) -> tuple:
        def parse_template(template_path):
            with open(template_path, 'r') as file:
                content = file.read()
            template_vars = set(re.findall(r'{{\s*instructs\.io\.(\w+)', content))
            included_templates = set(re.findall(r'{%\s*include\s*[\'"](.+?)[\'"]', content))
            for sub_template in included_templates:
                sub_path = os.path.join(os.path.dirname(template_path), sub_template)
                if os.path.exists(sub_path):
                    sub_vars, sub_includes = parse_template(sub_path)
                    template_vars.update(sub_vars)
                    included_templates.update(sub_includes)
            return template_vars, included_templates
        return parse_template(template_path)

    def check_template(self, *args, **kwargs):
        template_vars, included_templates = self.load_and_extract_vars(*args, **kwargs)
        class_fields = set(self.__annotations__.keys())
        missing_in_template = class_fields - template_vars - tech_fields
        missing_in_class = template_vars - class_fields
        if missing_in_template:
            print(
                f"{Fore.YELLOW}IoFields CONFIGURATION WARNING:{Fore.RESET} "
                f"Fields missing in template: {Fore.YELLOW}"
                f"{', '.join(missing_in_template)}{Fore.RESET}"
            )
        if missing_in_class:
            print(
                f"{Fore.YELLOW}IoFields CONFIGURATION WARNING:{Fore.RESET} "
                f"Fields missing in IoFields class: {Fore.YELLOW}"
                f"{', '.join(missing_in_class)}{Fore.RESET}"
            )

