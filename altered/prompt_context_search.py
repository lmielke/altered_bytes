# prompt_context_search.py


from altered.search_engine_cleaned import CleanWebSearch
from colorama import Fore, Style

class ContextSearch:

    template_name = 'i_context_search.md'

    def __init__(self, name:str, *args, **kwargs):
        self.context = {}
        self.se = CleanWebSearch(*args, name='search', **kwargs)

    def __call__(self, *args, **kwargs):
        results = self.get_search_results(*args, **kwargs)
        return self.mk_context(results, *args, **kwargs)

    def get_search_results(self, *args, search_query:str=None, **kwargs):
        if search_query is None:
            return {}
        self.context['search_query'] = search_query
        return self.se(*args, search_query=search_query, **kwargs)

    def mk_context(self, results, *args, search_results:list=None, strat_templates:list={}, 
        **kwargs):
        results = results if results else search_results
        if any([t.startswith('agg_') for t in strat_templates]) and len(results) >= 2:
            search_results = [results[-2]]
        else:
            search_results = results
        self.context['search_results'] = search_results
        return self.context