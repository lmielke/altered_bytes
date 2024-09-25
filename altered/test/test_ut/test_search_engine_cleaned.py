# test_search_engine_cleaned.py

import os, re, shutil, sys, time, yaml
import unittest
from colorama import Fore, Style

# test package imports
import altered.settings as sts
import altered.hlp_printing as hlpp

from altered.search_engine_cleaned import CleanWebSearch

class Test_CleanWebSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        with open(os.path.join(sts.test_data_dir, "test_search_engine_cleaned.yml"), "r") as f:
            out = yaml.safe_load(f)
        return out

    def test___init__(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test___call__(self, *args, **kwargs):
        test_data = self.test_data.copy()
        del test_data['content']
        search = CleanWebSearch(**test_data)
        results, search_query = search.__call__(**test_data)
        print(f"\n\n\n{Fore.GREEN}test___call__.search_query:{Fore.RESET} {search_query}")
        print(f"\n\n\n{Fore.GREEN}test___call__.results{Fore.RESET}: \n{results}")

    def test_cleaning(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    # def test_mk_context(self, *args, **kwargs):
    #     # self.test_data['responses'] = [self.test_data['content']]
    #     search = CleanWebSearch(**self.test_data)
    #     context = search.mk_context(**self.test_data)
    #     print(context)

if __name__ == "__main__":
    unittest.main()
