# prompt_context_search.py


from altered.search_engine_cleaned import CleanWebSearch
from colorama import Fore, Style

class ContextSearch:

    template_name = 'i_context_search.md'

    def __init__(self, name:str, *args, **kwargs):
        self.context = {}
        self.search = CleanWebSearch(*args, name='search', **kwargs)

    def __call__(self, *args, **kwargs):
        results = self.get_search_results(*args, **kwargs)
        return self.mk_context(results, *args, **kwargs)

    def get_search_results(self, *args, search_query:str=None, 
                                        run_search:bool=False,
                                        search_results:dict={},
                                        repeats:dict=None,
                                        **kwargs
        ):
        """
        Takes a search query and returns search results.
        The search results can be provided as an argument.
        """
        self.context['search_query'] = search_query
        # repeats dict contains the aggregation strategy used to condense the search results
        if repeats:
            if repeats.get('agg').startswith('agg_'):
                for entry in search_results:
                    # we only want to select the aggregation record in here
                    # it will contain the aggregation strategy inside the strat_template field
                    entries = [e.strip() for e in entry.get('content').split('\\n')]
                    entry['content'] = '\n'.join(entries)
                    if entry.get('strat_template') == repeats.get('agg'):
                        # we will latter use this in the render class to condition the text
                        entry.update(repeats)
                        return [entry]
        return search_results

    def mk_context(self, results, *args, **kwargs):
        self.context['search_results'] = results
        return self.context