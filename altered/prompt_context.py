"""
prompt.py

"""

from altered.search_engine_cleaned import CleanWebSearch

class Context:

    def __init__(self, name:str, context:str={}, *args, **kwargs):
        self._data = context
        self.ws = CleanWebSearch(*args, name=name, **kwargs)

    def __call__(self, *args, **kwargs):
        self.prep_data(*args, **kwargs)
        return self._data

    def prep_data(self, *args, context_history:list=None,**kwargs):
        self._data['context_history'] = self.get_history(*args, **kwargs)
        self._data['init_prompt'] = self.get_init_prompt(*args, **kwargs)
        search_results, search_query = self.get_search_results(*args, **kwargs)
        self._data['context_search_results'] = search_results
        self._data['context_search_query'] = search_query
                                                    

    def get_search_results(self, *args, context_search_results:list=None,
                                        context_search_query:list=None, **kwargs):
        if context_search_query is None:
            if context_search_results is None:
                return None, None
            else:
                return context_search_results, None
        results = self.ws(context_search_query, *args, **kwargs)
        return results
    
    def get_history(self, *args, context_history:list=None, **kwargs):
        self._data['context_history'] = context_history

    def get_init_prompt(self, *args, init_prompt:str=None, context:dict={}, **kwargs):
        if init_prompt is None:
            init_prompt = context.get('init_prompt', None)
        self._data['init_prompt'] = init_prompt


    @property
    def data(self, *args, **kwargs):
        return self._data
