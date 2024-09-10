# test_labeled_data_frame.py
import json, os, re, shutil, sys, time, yaml
import unittest
import pandas as pd
# test package imports
import altered.settings as sts
from altered.labeled_data_frame import LabeledDataFrame

class Test_LabeledDataFrame(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.test_data_path = os.path.join(sts.test_data_dir, 'test_labled_data_frame.yml')
        cls.test_data = cls.mk_test_data(*args, **kwargs)
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

    def test__constructor(self, *args, **kwargs):
        # Create a DataFrame using the fields from the YAML file
        df_data = {field: [None] for field in self.test_data.keys()}
        df = LabeledDataFrame(df_data)
        self.assertIsInstance(df, LabeledDataFrame)
        self.assertIsInstance(df, pd.DataFrame)

    def test___init__(self, *args, **kwargs):
        # Test initialization of LabeledDataFrame using fields from the YAML file
        df_data = {field: [None] for field in self.test_data.keys()}
        df = LabeledDataFrame(df_data)
        self.assertEqual(df.shape[1], len(self.test_data))
        self.assertEqual(set(df.columns), set(self.test_data.keys()))

    def test_add_description(self, *args, **kwargs):
        # Create a DataFrame using the fields from the YAML file
        df_data = {field: [None] for field in self.test_data.keys()}
        df = LabeledDataFrame(df_data)

        # Add descriptions
        df.fields.add_labels(   name='Unittest',
                                labels=self.test_data_path, 
                                description="Test DataFrame"
                                )

        print(df.fields.describe())

if __name__ == "__main__":
    unittest.main()