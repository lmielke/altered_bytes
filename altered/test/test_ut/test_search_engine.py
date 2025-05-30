import os
import unittest
import time

# Assuming sts is correctly defined in altered.settings
import altered.settings as sts
from altered.search_engine import WebSearch  # Import WebSearch class


class Test_WebSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.search_query = "monitor gpu performance powershell"
        cls.test_data_dir = sts.test_data_dir  # Assuming test_data_dir is set in settings
        cls.name = "Ut_Test_WebSearch"
        cls.data_dir = sts.test_data_dir
        cls.ws = WebSearch(name=cls.name, data_dir=cls.data_dir)  # Instantiate the WebSearch class
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.se_num = 3
        
        # Perform the search once and store the results
        # cls.ws.run_google_se(cls.search_query, se_num=cls.se_num)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    # def test___init__(self, *args, **kwargs):
    #     """
    #     Test if the WebSearch class initializes properly.
    #     """
    #     self.assertIsInstance(self.ws, WebSearch)

    def test___call__(self, *args, **kwargs):
        # ws = WebSearch(name=self.name, data_dir=self.data_dir)
        ws = WebSearch(name=self.name, data_dir=self.data_dir)
        ws(self.search_query, se_num=self.se_num, verbose=self.verbose)
        ws.results_to_table(verbose=self.verbose, max_files=6)
        ws.search_results.show(verbose=self.verbose)

if __name__ == "__main__":
    unittest.main()
