import os
import requests
import pandas as pd
from colorama import Fore

from altered.search_engine import WebSearch

from altered.model_connect import ModelConnect
from altered.renderer import Render
from altered.prompt_instructs import Instructions

class CleanWebSearch(WebSearch):

    default_repeats = {'num': 1, 'agg': 'agg_mean'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assi = ModelConnect(*args, **kwargs)
        # prompt constructor for LLM interaction
        self.insts = Instructions(*args, **kwargs)
        self.renderer = Render(*args, **kwargs)


    def __call__(self, *args, name:str=None, fmt:str=None, repeats:str=None, **kwargs):
        se_results, search_query = super().__call__(*args, **kwargs)
        if repeats is None: repeats = self.default_repeats
        cleaned = self.cleaning(se_results, *args, repeats=repeats, **kwargs)
        if repeats is not None and 'agg_mean' == repeats['agg']:
            print(f"{Fore.GREEN}Aggregating Cleaned Search Results: {Fore.RESET}: {repeats = }")
            # the second last record contains the aggregation
            se_results[0]['content'] = cleaned[-2].get('response').strip()
            se_results = [se_results[0]]
        else:
            print(f"{Fore.GREEN}Looping Cleaned Search Results: {Fore.RESET}: {repeats = }")
            for i, clean in enumerate(cleaned):
                _clean = clean.get('response').strip()
                se_results[i]['content'] = _clean
        return se_results, search_query
    
    def cleaning(self, se_results:dict, *args, alias='l3:8b_1', **kwargs):
        contents = []
        
        for i, result in enumerate(se_results):
            contents.append(self.mk_context(result.get('content'), *args, **kwargs))
        # we use the ModelConnect object to post the contents to the AI model
        r = self.assi.post(contents, *args, alias=alias, **kwargs )
        return r.get('responses')

    def mk_context(self, content:str, *args, user_prompt:str, search_query:str, **kwargs):
        _context = {
                    'responses': [content.replace('\n\n', '\n')],
                    'fmt': 'markdown',
                    'search_query': search_query,
                    'user_prompt': user_prompt,
        }
        # we use the Instructions object to render the context
        context = self.insts(strat_templates=['reduce_text'], **_context)
        rendered = self.renderer.render(
                                            template_name='instructs_strats.md',
                                            context = {'instructs': context},
                                            )
        print(f"{Fore.GREEN}\nrender result:{Fore.RESET} \n{rendered}")