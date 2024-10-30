import altered.settings as sts
import altered.hlp_printing as hlpp

from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from colorama import Fore
import requests

class Parser:
    """
    Parses content from a list of URLs, handling JavaScript-rendered content using Playwright.
    """

    def __init__(self, *args, **kwargs):
        pass

    def parse_site(self, url:str, timeout:int=10, *args, use_pwr:bool=True, **kwargs) -> str:
        """
        Fetches and parses the content from a given URL. If `use_pwr` is True, 
        it will use Playwright for JavaScript-rendered content.
        """
        try:
            if use_pwr:
                return self.fetch_with_playwright(url, *args, **kwargs)
            else:
                return self.fetch_with_requests(url, timeout=timeout)
        except Exception as e:
            print(f"{Fore.RED}Failed to fetch content from {url}: {e}{Fore.RESET}")
            return "Failed to fetch content."

    def fetch_with_requests(self, url:str, timeout:int=10) -> str:
        """
        Fetches content from a URL using requests.
        """
        print(f"\tRequests, Fetching content from {Fore.MAGENTA}{url} ...{Fore.RESET}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return self.extract_content(response.content)

    def fetch_with_playwright(self, url: str, *args, **kwargs) -> str:
        """
        Fetches content from a URL using Playwright to render JavaScript.
        """
        print(f"\tPlaywright, Parsing: {Fore.MAGENTA}{url} ...{Fore.RESET}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state('networkidle')  # Wait for network to be idle
            content = page.content()
            browser.close()
            return self.extract_content(content, *args, **kwargs)

    def extract_content(self, html_content:str, *args, verbose:int=0, **kwargs) -> str:
        """
        Extracts both paragraph text and code snippets from the HTML content.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        # Extract text from <p>, <pre>, and <code> tags
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        code_blocks = [code.get_text() for code in soup.find_all(['pre', 'code'])]
        # Combine the paragraphs and code blocks
        combined_content = '\n'.join(paragraphs + code_blocks)
        combined_content = self.clean_text(combined_content, *args, **kwargs)
        if verbose >= 2:
            print(f"\nsearch_parser.extract_content:")
            print(f"{Fore.MAGENTA}{combined_content}{Fore.RESET}")
        return combined_content if combined_content else "No readable content found."

    def parse_urls(self, urls:dict, *args, max_workers:int=5, verbose:int=0, **kwargs, ) -> dict:
        """
        Parses multiple URLs in parallel and updates the provided dictionary with parsed content.
        """
        def process_url(url):
            return url, self.parse_site(url, *args, verbose=verbose, **kwargs)
        url_contents = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(process_url, url): url for url in urls}
            for future in as_completed(future_to_url):
                url, parsed_content = future.result()
                url_contents[url] = parsed_content
        if verbose >= 2:
            print(f"search_parser.parse_urls:")
            print(f"{Fore.MAGENTA}{url_contents}{Fore.RESET}")
        return url_contents

    def clean_text(self, text:str, *args, **kwargs) -> str:
        """
        Cleans the text by removing extra whitespace and newlines.
        """
        clean_terms = {'Cookie duration', 'Data collected and processed', 'use cookies',
                        'Content presented to you on this service',
                        'Information regarding which advertising',
                        'Advertising presented to you',
                        'Cookies, device or similar online',
                        'Uses other forms of storage',
                        }
        cleaned, extender, last_line, cleaned_len = [], '', '', 0
        for line in text.split('\n'):
            line = line.strip()
            if not line or line == last_line:
                continue
            if any(term in line for term in clean_terms):
                continue
            if len(line) <= 3 or len(line.split(' ')) <= 2:
                nl = f" {line}" if len(line) > 1 else line
                if not extender:
                    extender = nl
                else:
                    extender += nl
                continue
            elif extender:
                cleaned.append(f" {extender}")
                cleaned_len += len(extender)
                extender = ''
                continue
            last_line = line
            cleaned.append(line)
            cleaned_len += len(line)
            if cleaned_len > sts.global_max_token_len:
                break
        return '\n'.join(cleaned)