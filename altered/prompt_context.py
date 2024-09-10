"""
prompt.py

"""

class Context:

    def __init__(self, context:str=None, *args, **kwargs):
        self._data = context if context is not None else ''

    def __call__(self, *args, **kwargs):
        self.prep_data(*args, **kwargs)
        return self

    def prep_data(self, *args, context:str='', **kwargs):
        self._data = context if context else None

    @property
    def data(self, *args, **kwargs):
        return self._data
