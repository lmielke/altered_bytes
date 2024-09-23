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

    def parse_site(self, url: str, use_playwright: bool = True, timeout: int = 10, *args, **kwargs) -> str:
        """
        Fetches and parses the content from a given URL. If `use_playwright` is True, 
        it will use Playwright for JavaScript-rendered content.
        """
        try:
            if use_playwright:
                return self.fetch_with_playwright(url)
            else:
                return self.fetch_with_requests(url, timeout=timeout)
        except Exception as e:
            print(f"{Fore.RED}Failed to fetch content from {url}: {e}{Fore.RESET}")
            return "Failed to fetch content."

    def fetch_with_requests(self, url: str, timeout: int = 10) -> str:
        """
        Fetches content from a URL using requests.
        """
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return self.extract_content(response.content)

    def fetch_with_playwright(self, url: str) -> str:
        """
        Fetches content from a URL using Playwright to render JavaScript.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state('networkidle')  # Wait for network to be idle
            content = page.content()
            browser.close()

            return self.extract_content(content)

    def extract_content(self, html_content: str) -> str:
        """
        Extracts both paragraph text and code snippets from the HTML content.
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract text from <p>, <pre>, and <code> tags
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        code_blocks = [code.get_text() for code in soup.find_all(['pre', 'code'])]

        # Combine the paragraphs and code blocks
        combined_content = '\n'.join(paragraphs + code_blocks)

        return combined_content if combined_content else "No readable content found."

    def parse_urls(self, urls: dict, max_workers: int = 5, use_playwright: bool = True, *args, **kwargs) -> dict:
        """
        Parses multiple URLs in parallel and updates the provided dictionary with parsed content.
        """
        def process_url(url):
            return url, self.parse_site(url, use_playwright=use_playwright, *args, **kwargs)

        print(f"{Fore.YELLOW}Parsing {len(urls)} URLs in parallel...{Fore.RESET}")
        url_contents = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(process_url, url): url for url in urls}
            for future in as_completed(future_to_url):
                url, parsed_content = future.result()
                url_contents[url] = parsed_content

        return url_contents
