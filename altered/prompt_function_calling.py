"""
prompt_function_calling.py
AI function calling
"""


import json
import os
import importlib
from typing import List
from colorama import Fore
import altered.settings as sts


class Function:
    """
    Manages OpenAI tool functions using JSON schema stored in `sts.apis_json_dir`.
    Supports extracting tools for prompts and executing matched function calls.
    """

    def __init__(self, *args, f_type: str = "function", **kwargs):
        self.name = None
        self.arguments = {}
        self.results = None
        self.type = f_type
        self.tools = []
        self.names = []
        self.executables = {}
        self.executable = None
        self.is_safe = False
        self.exe_out = {"status": None, "body": None}

    def get_function_data(self, *args, **kwargs) -> List[dict]:
        """
        Load all OpenAI tool definitions for use in the chat prompt.
        Returns a list of OpenAI-compatible function schemas.
        """
        for json_obj in self.load_apis_json(*args, **kwargs):
            openai_meta = json_obj["openai"]
            base_meta = json_obj.get("base", {})
            exec_meta = json_obj.get("execution", {})

            self.append_executables(openai_meta, base_meta, exec_meta)

            openai_meta.pop("body", None)
            short_name = openai_meta["name"].split(".")[-1]
            openai_meta["name"] = short_name
            self.names.append(short_name)

            self.tools.append({"type": self.type, "function": openai_meta})

        return self.tools

    def append_executables(self, func_meta: dict, base_meta: dict, exec_meta: dict):
        """
        Store execution info needed to import and call a function later.
        """
        fq_name = func_meta["name"]                # e.g. Devices.toggle_device
        class_name, fn_name = fq_name.split(".")   # e.g. Devices, toggle_device
        import_path = base_meta.get("import_path") or exec_meta.get("import_path")

        self.executables[fn_name] = {
            "fq_name": fq_name,
            "class_name": class_name,
            "import_path": import_path,
        }

    def load_apis_json(self, *args, **kwargs):
        """
        Load all tool JSON schemas from the configured API directory.
        """
        contents = []
        for filename in os.listdir(sts.apis_json_dir):
            if filename.endswith(".json") and not filename.startswith("#"):
                path = os.path.join(sts.apis_json_dir, filename)
                with open(path, "r") as file:
                    contents.append(json.load(file))
        return contents

    def get_func_call(self, tool_calls: list = None, *args, **kwargs):
        """
        Parse tool call and store name and arguments for later execution.
        """
        if not tool_calls:
            return None

        args_obj = json.loads(tool_calls[0].function.arguments)
        for k, v in args_obj.items():
            self.arguments[k] = v.strip() if isinstance(v, str) else v

        self.name = tool_calls[0].function.name
        self.executable = self.executables.get(self.name)
        self.is_safe = self.inspect_function(*args, **kwargs)
        return True

    def inspect_function(self, *args, **kwargs):
        """
        Placeholder for future safety checks.
        """
        return True

    def execute(self, *args, **kwargs):
        if not self.executable:
            return None

        mod_path = self.executable["import_path"]
        cls_name = self.executable["class_name"]
        fn_name = self.name

        module = importlib.import_module(mod_path)
        cls = getattr(module, cls_name)
        result = getattr(cls, fn_name)(**self.arguments)

        out = result if isinstance(result, dict) else {"status": result, "body": None}
        out["msg"] = (
            f"{Fore.GREEN if out.get('status') else Fore.RED}"
            f"Function executed: {fn_name}{Fore.RESET}"
        )
        return out
