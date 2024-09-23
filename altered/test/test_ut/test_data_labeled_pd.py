# test_data_labeled_df.py
import os, re, shutil, sys, time, yaml
import unittest
import pandas as pd
from colorama import Fore, Style
# test package imports
import altered.settings as sts

import altered.data_labeled_pd as lpd

class Test_LabeledPandas(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.fields_path = os.path.join(sts.data_dir, 'data__data_load_fields_default.yml')
        # cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        test_data = None
        with open(cls.test_data_path, "r") as f:
            test_data = yaml.safe_load(f)
        return test_data

    def test___init__(self, *args, **kwargs):
        # Test initialization of LabeledPandas using fields from the YAML file
        df = lpd.DataFrame(fields_path=self.fields_path)()
        print(f"df: {df}")



if __name__ == "__main__":
    unittest.main()
