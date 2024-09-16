import os, requests, yaml
from bs4 import BeautifulSoup
import pandas as pd
from colorama import Fore

from altered.data_vectorized import VecDB
from altered.model_params import config as mpg
import altered.settings as sts
import altered.hlp_printing as hlpp
from tabulate import tabulate as tb


class WebSearch:
    """
    Takes a search query and performs a Google search, then parses the search results.
    """
    # fields = {'kind', 'title', 'source', 'displayLink', 'snippet', 'pagemap', 'content'}
    fields_path = os.path.join(sts.data_dir, 'search_engine__WebSearch_search_fields.yml')

    def __init__(self, *args, name: str = None, **kwargs):
        self.name = name
        print(f"Initializing WebSearch instance {mpg.services = }")
        self.api_key = mpg.services.get('google_se').get('api_key')
        self.cse_id = mpg.services.get('google_se').get('cse_id')
        self.url = mpg.services.get('google_se').get('url')
        # Holds the search results in a list of dicts, which will later be loaded into a dataframe
        self.r = {}
        self.results = []
        self.data = VecDB(*args, name=name, fields_path=self.fields_path, **kwargs)

    def __call__(self, *args, **kwargs):
        self.run_google_se(*args, **kwargs)
        self.filter_fields(*args, **kwargs)
        self.append_records(*args, **kwargs)
        self.parse_urls(*args, **kwargs)
        # hlpp.records_to_table(self.r.get('context').get('title'), self.results, color=Fore.RED, max_chars=120)

    def run_google_se(self, query: str, num: int = 10, *args, **kwargs) -> dict:
        """
        Performs a Google Custom Search and returns the results as a JSON dictionary.
        """
        params = {'key': self.api_key, 'cx': self.cse_id, 'q': query, 'num': num}
        r = requests.get(self.url, params=params, *args, **kwargs)
        r.raise_for_status()
        self.r = r.json()

    def filter_fields(self, *args, **kwargs):
        map_fields = self.data.mfields
        for item in self.r.get('items', []):
            record = {}
            for k, vs in item.items():
                if k in map_fields:
                    record[k] = vs
            record['content'] = None
            self.results.append(record)

    def append_records(self, *args, **kwargs):
        for result in self.results:
            self.data.append(result, *args, **kwargs)
        # self.data.show()

    def parse_site(self, url: str, *args, **kwargs) -> str:
        """
        Fetches and parses the content from a given URL.
        Filters out invalid parameters for requests.get() from kwargs.
        """
        try:
            # Remove any irrelevant arguments like 'num' before passing to requests.get()
            valid_kwargs = {k: v for k, v in kwargs.items() if k in ['headers', 'timeout', 'auth', 'cookies', 'proxies']}

            response = requests.get(url, *args, **valid_kwargs)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract main text content from <p> tags as a simple approach
            paragraphs = [p.get_text() for p in soup.find_all('p')]
            return '\n'.join(paragraphs) if paragraphs else "No readable content found."
            
        except requests.RequestException as e:
            print(f"{Fore.RED}Failed to fetch content from {url}: {e}{Fore.RESET}")
            return "Failed to fetch content."



    def parse_urls(self, *args, **kwargs):
        """
        Iterates through self.data.ldf, fetches and parses the 'source' (URL) field,
        and writes the parsed text to the 'content' field.
        """
        for index, row in self.data.ldf.iterrows():
            url = row.get('source')
            
            # Properly handle missing values (NA or NaN)
            if pd.notna(url) and url:
                print(f"{Fore.YELLOW}Parsing content from: {url}{Fore.RESET}")
                parsed_content = self.parse_site(url, *args, **kwargs)

                # Update the 'content' field in the dataframe with the parsed content
                self.data.ldf.at[index, 'content'] = parsed_content
            else:
                print(f"{Fore.RED}Skipping empty or invalid URL at index {index}{Fore.RESET}")

        print(f"{Fore.GREEN}Content parsed for all valid URLs.{Fore.RESET}")
