"""
prompt_context.py
This is the last change I made.
"""
from altered.prompt_context_search import ContextSearch
from altered.prompt_context_activities import ContextActivities
from altered.prompt_context_sys_info import ContextSysInfo
from altered.prompt_context_package_data import ContextPackageData
from colorama import Fore, Style


class Context:

    def __init__(self, name:str, context:str={}, *args, **kwargs):
        self.context = context
        self.web_search = ContextSearch(*args, name=name, **kwargs)
        self.user_infos = ContextActivities(*args, **kwargs)
        self.os_sys_info = ContextSysInfo(*args, **kwargs)
        self.pg_info = ContextPackageData(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.prep_data(*args, **kwargs)
        return self.context

    def prep_data(self, *args, **kwargs):
        self.get_history(*args, **kwargs)
        self.get_init_prompt(*args, **kwargs)
        self.context.update(self.web_search(*args, **kwargs))
        self.get_sys_info(*args, **kwargs)

    def get_sys_info(self, *args,   package_info:bool=False, 
                                    sys_info:bool=False, 
                                    user_info:bool=False, 
        **kwargs):
        if sys_info:
            self.context.update(self.os_sys_info.mk_context(*args, sys_info=sys_info, **kwargs))
        if package_info:
            self.context.update(self.pg_info.mk_context(*args, package_info=package_info, **kwargs))
        if user_info:
            self.context.update(self.user_infos(*args, user_info=user_info, **kwargs))

    def get_history(self, *args, chat_history:list=None, **kwargs):
        if chat_history:
            self.context['chat_history'] = chat_history

    def get_init_prompt(self, *args, init_prompt:str=None, context:dict={}, **kwargs):
        if init_prompt is None:
            init_prompt = context.get('init_prompt', None)
        if init_prompt:
            self.context['init_prompt'] = init_prompt

    @property
    def data(self, *args, **kwargs):
        return self.context
