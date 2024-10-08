# prompt_context_search.py


from altered.search_engine_cleaned import CleanWebSearch
from colorama import Fore, Style

class ContextSearch:

    template_name = 'i_context_search.md'

    def __init__(self, name:str, *args, **kwargs):
        self.context = {}
        self.se = CleanWebSearch(*args, name='search', **kwargs)

    def get_search_results(self, *args, search_query:list=None, **kwargs):
        if search_query is None:
            return {}
        results = self.se(*args, search_query=search_query, **kwargs)
        self.context['search_results'] = results
        self.context['search_query'] = search_query
        return self.context