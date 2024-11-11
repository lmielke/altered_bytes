"""
search_engine_cleaned.py
Takes a search query as you would type it into Google and returns the 
search results. We use the returned links to parse the web-sites contents
"""

import os
import requests
import pandas as pd
from colorama import Fore, Style


import altered.hlp_printing as hlpp
from altered.search_engine import WebSearch
from altered.model_connect import SingleModelConnect
from altered.renderer import Render
from altered.prompt_instructs import Instructions

class CleanWebSearch(WebSearch):

    default_repeats = {'num': 1, 'agg': None}
    # we use clean_text to clean the search results
    strat_template = 'clean_text'
    # we use search.md to render the clean_text prompt for the model
    render_template = 'search.md'
    alias = 'l3.2_0'

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
        # Note, self.clean_search_results is doing a ollama call
        cleaned = self.clean_search_results(*args, repeats=repeats, **kwargs)
        for i, clean in enumerate(cleaned):
            # print(f"\n\n{Fore.RED}CleanWebSearch {i}:{Fore.RESET} {clean = }")
            if clean.get('strat_template') is not None:
                self.r.append(self.r[0].copy())
                self.r[-1]['content'] = clean.get('response').strip()
                self.r[-1]['short'] = ''
                self.r[-1]['strat_template'] = clean.get('strat_template')
            else:
                self.r[i]['short'] = clean.get('response').strip()
            self.r[i]['source'] = self.r[i].get('link')
        return self.r

    def clean_search_results(self, *args, alias=None, **kwargs):
        """
        Note: we pull the alias here, because we replace it with the default alias.
        """
        contents = []
        # we iterate over the search results and create a claning prompt for every single one
        for i, result in enumerate( self.r ):
            contents.append(self.mk_prompt( result.get('content'), result.get('link'), *args,
                                            **kwargs,
                            )
            )
        # we use the ModelConnect object to post the contents to the AI model
        # NOTE: due to the potentially giant context size we have to use a powerfull server
        return self.assi.post(contents, *args, alias=self.alias, **kwargs ).get('responses')

    def mk_prompt(self, content:str, link:str, search_query:str, *args, 
                                    user_prompt:str, **kwargs,
        ) -> str:
        _context = {    'responses': [content.replace('\n\n', '\n')],
                        'fmt': 'markdown',
                        'link': link,
                        'search_query': search_query,
                        'user_prompt': user_prompt,
        }
        # we use the Instructions object to render the context
        context = self.insts(strat_template=self.strat_template, **_context).context
        rendered = self.renderer.render(*args,
                                        template_name=self.render_template,
                                        context = { 'instructs': context,
                                                    'prompt_title': 'Clean Up Search Results',
                                                    },
                                        **kwargs,
                                        )
        return rendered