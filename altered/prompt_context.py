"""
prompt.py

"""
from altered.prompt_context_search import ContextSearch
from colorama import Fore, Style

class Context:

    def __init__(self, name:str, context:str={}, *args, **kwargs):
        self.context = context
        print(f"{Fore.CYAN}{Style.BRIGHT}Context.__init__.in {name = }:\n{kwargs = }{Style.RESET_ALL}")
        self.se = ContextSearch(*args, name=name, **kwargs)
        print(f"{Fore.CYAN}{Style.BRIGHT}Context.__init__.out {name = }:\n{kwargs = }{Style.RESET_ALL}")

    def __call__(self, *args, **kwargs):
        self.prep_data(*args, **kwargs)
        return self.context

    def prep_data(self, *args, chat_history:list=None, **kwargs):
        self.context['chat_history'] = self.get_history(*args, **kwargs)
        self.context['init_prompt'] = self.get_init_prompt(*args, **kwargs)
        self.context.update(self.se.get_search_results(*args, **kwargs))
    
    def get_history(self, *args, chat_history:list=None, **kwargs):
        self.context['chat_history'] = chat_history

    def get_init_prompt(self, *args, init_prompt:str=None, context:dict={}, **kwargs):
        if init_prompt is None:
            init_prompt = context.get('init_prompt', None)
        self.context['init_prompt'] = init_prompt

    @property
    def data(self, *args, **kwargs):
        return self.context
