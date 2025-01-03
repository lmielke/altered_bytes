import os
import requests
import pandas as pd
from colorama import Fore

# from altered.data_vectorized import VecDB
from altered.data import Data
from altered.model_params import config as config
import altered.settings as sts
import altered.hlp_printing as hlpp
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
        self.api_key = config.services.get('google_se').get('api_key')
        self.cse_id = config.services.get('google_se').get('cse_id')
        self.g_url = config.services.get('google_se').get('url')
        self.search_results = Data(*args, 
                    name=name, 
                    u_fields_paths=[self.search_fields_path], 
                    data_dir = data_dir if data_dir is not None else self.default_data_dir,
                    **kwargs)
        self.parser = Parser(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        se_results = self.run_google_se(*args, **kwargs)
        urls = [l.get('link') for l in se_results.get('items')]
        se_contents = self.parser.parse_urls(urls, *args, max_workers=5, **kwargs)
        self.r = self.prep_results(se_results, se_contents, urls, *args, **kwargs )
        return self.r

    def results_to_direct_output(self, search_query:str, *args, fields=['source', 'content'], 
        **kwargs):
        # we use self.search_results.ldf.iterrows to get the data for provided fields as dict
        dr = [{f: r[f] for f in fields} for i, r in self.search_results.ldf[1:].iterrows()]
        return dr, search_query

    def run_google_se(self, search_query: str, se_num: int = None, *args, **kwargs) -> dict:
      """
      Performs a Google Custom Search and returns the results as a JSON dictionary.
      """
      se_num = se_num if se_num is not None else self.se_num
      params = {
                  'key': self.api_key,
                  'cx': self.cse_id,
                  'q': search_query,
                  'num': se_num,
                  'lang': 'en'  # Add the 'lang' parameter with value 'en' for English
      }
      print(f"Performing Search for query:{Fore.YELLOW} '{search_query}' {Fore.RESET}")
      r = requests.get(self.g_url, params=params)
      r.raise_for_status()
      return r.json()

    def prep_results(self, se_results:dict, se_contents:dict, urls:list, search_query:str, *args, **kwargs):
        """
        Filters the search results to only include relevant fields.
        """
        # field mapping is expensive, so do it only once before the loop
        # map_fields = self.search_results.mfields
        r = []
        for i, (url, item) in enumerate(zip(urls, se_results.get('items'))):
            # here we filter some values for the data record by using the columns property
            record = {k: vs for k, vs in item.items() if k in self.search_results.columns}
            record['content'] = se_contents[item.get('link')]
            record['search_query'] = search_query
            record['link'] = url
            r.append(record)
        return r

    def results_to_table(self, r:list=None, *args, **kwargs):
        """
        Appends filtered search results to the internal VecDB object.
        """
        r = r if r is not None else self.r
        for result in r:
            self.search_results.append(result, *args, **kwargs)
        self.search_results.save_to_disk(*args, **kwargs)
