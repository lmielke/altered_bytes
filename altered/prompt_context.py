"""
prompt_context.py
This is the last change I made.
"""
from altered.prompt_context_search import ContextSearch
from altered.prompt_context_activities import ContextActivities
from altered.prompt_context_os_system import ContextOsSystem
from altered.prompt_context_package_data import ContextPackageData
from colorama import Fore, Style


class Context:

    def __init__(self, name:str, context:str={}, *args, **kwargs):
        self.context = context
        self.se = ContextSearch(*args, name=name, **kwargs)
        self.ca = ContextActivities(*args, **kwargs)
        self.os = ContextOsSystem(*args, **kwargs)
        self.cpd = ContextPackageData(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.prep_data(*args, **kwargs)
        return self.context

    def prep_data(self, *args, chat_history:list=None, num_activities:int=0, **kwargs):
        self.context['chat_history'] = self.get_history(*args, **kwargs)
        self.context['init_prompt'] = self.get_init_prompt(*args, **kwargs)
        self.context.update(self.se.get_search_results(*args, **kwargs))
        self.context.update(self.os.mk_context(*args, **kwargs))
        self.context.update(self.cpd.mk_context(*args, **kwargs))
        if num_activities:
            self.context.update(self.ca.get_activities_results(*args, 
                                                    num_activities=num_activities, **kwargs))
    
    def get_history(self, *args, chat_history:list=None, **kwargs):
        self.context['chat_history'] = chat_history

    def get_init_prompt(self, *args, init_prompt:str=None, context:dict={}, **kwargs):
        if init_prompt is None:
            init_prompt = context.get('init_prompt', None)
        self.context['init_prompt'] = init_prompt

    @property
    def data(self, *args, **kwargs):
        return self.context
