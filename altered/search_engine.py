import os
import requests
import pandas as pd
from colorama import Fore

from altered.data_vectorized import VecDB
from altered.model_params import config as mpg
import altered.settings as sts
import altered.hlp_printing as hlpp
from tabulate import tabulate as tb
from altered.search_parser import Parser  # Importing Parser from the Parser module


class WebSearch:
    """
    Takes a search search_query and performs a Google search, then parses the search results.
    """
    # default_data_dir handles where table data are stored and loaded
    default_data_dir = os.path.join(sts.resources_dir, 'search')
    # search_fields_path is the path to the fields file for the table creator
    search_fields_path = os.path.join(sts.data_dir, 'data_WebSearch_search_fields.yml')
    se_num = 3


    def __init__(self, *args, name:str=None, data_dir:str=None, **kwargs):
        self.name = name
        self.api_key = mpg.services.get('google_se').get('api_key')
        self.cse_id = mpg.services.get('google_se').get('cse_id')
        self.g_url = mpg.services.get('google_se').get('url')
        self.search_results = VecDB(*args, 
                    name=name, 
                    u_fields_paths=[self.search_fields_path], 
                    data_dir = data_dir if data_dir is not None else self.default_data_dir,
                    **kwargs)
        self.parser = Parser()  # Instantiate the Parser class

    def __call__(self, *args, **kwargs):
        se_results = self.run_google_se(*args, **kwargs)
        self.urls = [l.get('link') for l in se_results.get('items')]
        se_contents = self.parser.parse_urls(self.urls, max_workers=5)
        self.results_to_table(  self.prep_results(
                                                    se_results, 
                                                    se_contents, 
                                                    *args, **kwargs
                                ), *args, **kwargs,
        )
        return self.results_to_direct_output(*args, **kwargs)

    def results_to_direct_output(self, search_query:str, *args, fields=['source', 'content'], **kwargs):
        # we use self.search_results.ldf.iterrows to get the data for provided fields as dict
        dr = [{f: r[f] for f in fields} for i, r in self.search_results.ldf[1:].iterrows()]
        return dr, search_query

    def run_google_se(self, search_query:str, num:int=None, *args, **kwargs) -> dict:
        """
        Performs a Google Custom Search and returns the results as a JSON dictionary.
        """
        num = num if num is not None else self.se_num
        params = {'key': self.api_key, 'cx': self.cse_id, 'q': search_query, 'num': num}
        print(f"{Fore.YELLOW}Performing Search for query: '{search_query}' {Fore.RESET}")
        r = requests.get(self.g_url, params=params)
        r.raise_for_status()
        return r.json()

    def prep_results(self, se_results:dict, se_contents:dict, *args, **kwargs):
        """
        Filters the search results to only include relevant fields.
        """
        # field mapping is expensive, so do it only once before the loop
        # map_fields = self.search_results.mfields
        r = []
        for i, (url, item) in enumerate(zip(self.urls, se_results.get('items'))):
            # here we filter some values for the data record by using the columns property
            record = {k: vs for k, vs in item.items() if k in self.search_results.columns}
            record['content'] = se_contents[item.get('link')]
            record['link'] = url
            r.append(record)
        return r

    def results_to_table(self, r:list, *args, **kwargs):
        """
        Appends filtered search results to the internal VecDB object.
        """
        for result in r:
            self.search_results.append(result, *args, **kwargs)
        self.search_results.save_to_disk(*args, **kwargs)


from altered.model_connect import ModelConnect

class CleanWebSearch(WebSearch):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assi = ModelConnect(*args, **kwargs)

    def __call__(self, *args, name:str=None, fmt:str=None, repeats:str=None, **kwargs):
        se_results, search_query = super().__call__(*args, **kwargs)
        cleaned = self.cleaning(se_results, search_query, *args, repeats=repeats, **kwargs)
        print(f"{Fore.YELLOW = } {Fore.RESET = }")
        if repeats is not None and 'prompt_aggregations' in repeats:
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
    
    def cleaning(self, se_results:dict, search_query:str, *args, repeats:dict=None, alias='l3:8b_1', **kwargs):
        contents = []
        for i, result in enumerate(se_results):
            contents.append(self.cleaning_prompt(result.get('content'), search_query))
        # we use the ModelConnect object to post the contents to the AI model
        if repeats is None: repeats = {'num': 1, 'agg': 'agg_mean'}
        r = self.assi.post(contents, *args, alias=alias, repeats=repeats, **kwargs )
        return r.get('responses')



    def cleaning_prompt(self, content:str, search_query:str, *args, **kwargs):
        return f"""
        <results>

        {content}

        </results>



        <INST>
        The <content> tag above contains search results from a Google search using the 
        
        search term: "{search_query}"
        
        The egerly parsed results text now contains a lot of unwanted information. 
        (i.e. ads, cookie data, storage data, etc.)
        Your task is to clean the results text and signifficantly reduce the text size. Do 
        only include text of high and medium relevace to search term.
        
        Return the cleaned results as nicely formatted 'markdown' text using English language. 
        Do not add any additional information! Do not add comments to your answer!
        </INST>
        """
