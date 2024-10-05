import os
import warnings
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, List
from colorama import Fore, Style

import altered.settings as sts
from altered.yml_parser import YmlParser

from altered.prompt_io_fields import IoFields


class Io:
    
    template_name = 'i_instructs_io.md'


    def __init__(self, *args, **kwargs):
        self.fields = None
        self.templates = {}
        self.io_type = None
        self.io_name = None
        self.template_name = None
        self.template_file_name = None
        self.template_path = None

    def __call__(self, *args, **kwargs):
        self.mk_io_params(*args, **kwargs)
        self.load_io(*args, **kwargs)
        result = self.mk_context(*args, **kwargs)
        return result

    def mk_io_params(self, io_template_name: str, *args, **kwargs):
        self.template_name = io_template_name
        self.template_file_name = f'{io_template_name}.yml'
        self.template_path = os.path.join(sts.io_dir, self.template_file_name)
        self.io_type, io_meth = io_template_name.split('_', 1)
        self.fields = IoFields(io_meth=io_meth, io_type=self.io_type)

    def load_io(self, *args, fmt='markdown', **kwargs):
        loader = YmlParser(*args, fields_paths=[self.template_path], **kwargs)
        self.fields.method = {
            'body': loader.describe(fmt=fmt),
            'meta': loader.fields.get('meta'),
        }
        for k, vs in loader.data.items():
            setattr(self.fields, k, vs)
        self.fields.fmt_comment = f"<!--, #..., >..."
        self.fields.fmt = fmt

    def mk_context(self, *args, fmt:str=None, **kwargs):
        if fmt is not None:
            self.fields.fmt = fmt
        return self.fields.__dict__

    def add_io(self, io_meth, value):
        setattr(self.fields, io_meth, value)
        self.fields.__post_init__()  # Re-run validation after adding a new field


class Default(Io):
    pass

class Simple(Io):
    pass