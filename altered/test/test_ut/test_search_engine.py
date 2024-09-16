import os
import re
import shutil
import sys
import time
import yaml
import unittest
from unittest.mock import patch

# Test package imports
import altered.settings as sts
from altered.search_engine import WebSearch

verbose = 2

class Test_WebSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.test_data_path = os.path.join(sts.test_data_dir, "search_engine_get_web_results.yml")
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        with open(cls.test_data_path, "r") as f:
            return yaml.safe_load(f)

    # @patch('altered.search_engine.WebSearch.get_web_results')
    # def test_get_web_results(self, mock_get_web_results, *args, **kwargs):
    #     # Mock the get_web_results method
    #     mock_get_web_results.return_value = self.test_data

    #     # Initialize the WebSearch class
    #     se = WebSearch(name="TestSearchEngine", *args, **kwargs)

    #     # Call the method with a test query
    #     query = "sky blue color reason"
    #     results = se.get_web_results(query, *args, **kwargs)

    #     # Assert that the results match the test data
    #     self.assertEqual(results, self.test_data)
    #     print("Test get_web_results passed.")

    # def test_parse_site(self, *args, **kwargs):
    #     # Initialize the WebSearch class
    #     se = WebSearch(name="TestSearchEngine", *args, **kwargs)

    #     # Use a sample URL from the test data
    #     sample_url = self.test_data['items'][0]['link']
    #     body = se.parse_site(sample_url, *args, **kwargs)

    #     # Since we cannot fetch actual content in testing, we'll skip real parsing
    #     # You might want to mock requests.get or adjust this test as needed
    #     self.assertIsInstance(body, str)
    #     print(f"Test parse_site passed.: {se.results}")

    # @patch('altered.search_engine.WebSearch.parse_site')
    # def test_append_to_results(self, mock_parse_site, *args, **kwargs):
    #     # Mock the parse_site method to return a sample body text
    #     mock_parse_site.return_value = "Sample body text."

    #     # Initialize the WebSearch class
    #     se = WebSearch(name="TestSearchEngine", *args, **kwargs)

    #     # Use a sample item from the test data
    #     sample_item = self.test_data['items'][0]
    #     se.append_to_results(sample_item, *args, **kwargs)

    #     # Assert that the result was added to self.results
    #     self.assertEqual(len(se.results), 1)
    #     self.assertEqual(se.results[0]['url'], sample_item['link'])
    #     self.assertEqual(se.results[0]['body'], "Sample body text.")
    #     print(f"Test append_to_results passed.: {se.results}")

    # def test___init__(self, *args, **kwargs):
    #     # Initialize the WebSearch class
    #     se = WebSearch(name="TestSearchEngine", *args, **kwargs)

    #     # Assert that the object was initialized correctly
    #     self.assertEqual(se.name, "TestSearchEngine")
    #     self.assertIsInstance(se.results, list)
    #     print(f"Test __init__ passed.: {se.results}")


    def test_real_search(self, *args, **kwargs):
        # Initialize the WebSearch class
        se = WebSearch(name="TestSearchEngine", *args, verbose=verbose, **kwargs)
        se("monitor gpu performance powershell", *args, num=3, **kwargs )
        se.data.show(verbose=2)


if __name__ == "__main__":
    unittest.main()
