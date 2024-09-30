"""
search_engine_cleaned.py
Takes a search query as you would type it into Google and returns the 
search results. We use the returned links to parse the web-sites contents
"""

import os
import requests
import pandas as pd
from colorama import Fore

from altered.search_engine import WebSearch

from altered.model_connect import SingleModelConnect
from altered.renderer import Render
from altered.prompt_instructs import Instructions

class CleanWebSearch(WebSearch):

    default_repeats = {'num': 1, 'agg': 'agg_mean'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assi = SingleModelConnect(*args, **kwargs)
        # prompt constructor for LLM interaction
        self.insts = Instructions(*args, **kwargs)
        self.renderer = Render(*args, **kwargs)
        self.r_cleaned = []


    def __call__(self, *args, name:str=None, fmt:str=None, repeats:str=None, **kwargs):
        # The super call already runs the search and parses the results
        super().__call__(*args, **kwargs)
        if repeats is None: repeats = self.default_repeats
        # Note, self.cleaning is doing a ollama call
        cleaned = self.cleaning(*args, repeats=repeats, **kwargs)
        if repeats is not None and 'agg_mean' == repeats['agg']:
            # We might want to aggregate multiple search results into a single RAG Info
            print(f"{Fore.GREEN}Aggregating Cleaned Results: {Fore.RESET}: {repeats = }")
            # the second last record contains the aggregation
            self.r_cleaned.append(self.r[0])
            self.r_cleaned[0]['content'] = cleaned[-2].get('response').strip()
        else:
            # Or, we want to keep all the search results seperate
            print(f"{Fore.GREEN}Looping Cleaned Results: {Fore.RESET}: {repeats = }")
            for i, clean in enumerate(cleaned):
                _clean = clean.get('response').strip()
                self.r_cleaned[i]['content'] = _clean
        return self.r_cleaned
    
    def cleaning(self, *args, alias='l3:8b_1', **kwargs):
        contents = []
        
        for i, result in enumerate(self.r):
            contents.append(self.mk_prompt(result.get('content'), result.get('link'), 
                                            *args, **kwargs))
        # we use the ModelConnect object to post the contents to the AI model
        r = self.assi.post(contents, *args, alias=alias, **kwargs )
        return r.get('responses')

    def mk_prompt(self, content:str, link:str, *args, user_prompt:str, search_query:str, 
        **kwargs):
        _context = {
                    'responses': [content.replace('\n\n', '\n')],
                    'fmt': 'markdown',
                    'link': link,
                    'search_query': search_query,
                    'user_prompt': user_prompt,
        }
        # we use the Instructions object to render the context
        context = self.insts(strat_templates=['reduce_text'], **_context)
        rendered = self.renderer.render(
                                            template_name='instructs_strats.md',
                                            context = {'instructs': context},
                                            )
        print(f"{Fore.GREEN}\nCleanWebSearch.mk_prompt:{Fore.RESET} \n{rendered}")
        return rendered