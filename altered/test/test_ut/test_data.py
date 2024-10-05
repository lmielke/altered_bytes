import os, re, shutil, sys, time, yaml
import unittest
import pandas as pd
from colorama import Fore, Style
# test package imports
import altered.settings as sts
from altered.data import Data

class Test_Data(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 2
        cls.test_data_dir = sts.test_data_dir
        cls.test_file_name = 'data_Data_load_fields_default.yml'
        cls.fields_path = os.path.join(sts.data_dir, cls.test_file_name)
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.name = 'UT_Test_Data'

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        # Load test data from the YAML file
        with open(cls.fields_path, 'r') as f:
            return yaml.safe_load(f)

    def test___init__(self, *args, **kwargs):
        # Test the initialization of the Data class
        data = Data(name=self.name, fields_paths=[self.fields_path], data_dir=sts.test_data_dir)
        self.assertEqual(data.name, self.name)

    def test_mk_data_dir(self, *args, **kwargs):
        # Test creation of the data directory
        data = Data(name=self.name, fields_paths=[self.fields_path], data_dir=sts.test_data_dir)
        expected_dir = os.path.join(sts.test_data_dir, self.name)
        self.assertTrue(os.path.exists(expected_dir))

    # def test_load_fields(self, *args, **kwargs):
    #     # Test loading fields from YAML file
    #     data = Data(name=self.name, fields_paths=[self.fields_path], data_dir=sts.test_data_dir)
    #     loaded_fields = data.load_fields(fields='data__data_load_fields_default.yml')
    #     self.assertEqual(loaded_fields, self.test_data)

    def test_create_table(self, *args, **kwargs):
        # Test the creation of the DataFrame with the correct columns
        data = Data(name=self.name, fields_paths=[self.fields_path], data_dir=sts.test_data_dir)
        data.create_table()
        self.assertFalse(data.ldf.empty)
        # self.assertListEqual(list(data.ldf.columns), list(self.test_data.keys()))

    def test_save_to_disk(self, *args, **kwargs):
        # Test saving the DataFrame to disk
        data = Data(name=self.name, fields_paths=[self.fields_path], data_dir=sts.test_data_dir)
        data.create_table()
        expected_file = f"{self.name}_{data.time_stamp.strftime(sts.time_strf)[:-7]}.csv"
        print(f"{expected_file = }")
        data.save_to_disk( data_file_name=expected_file, verbose=self.verbose)
        file_path = os.path.join(data.fs.data_dir, expected_file)
        print(f"{file_path = }")
        self.assertTrue(os.path.exists(file_path))

    def test_load_from_disk(self, *args, **kwargs):
        # Test loading the DataFrame from disk
        data = Data(name=self.name, fields_paths=[self.fields_path], data_dir=sts.test_data_dir)
        data.create_table()
        data.save_to_disk()
        data_file_name = f"{data.time_stamp.strftime(sts.time_strf)[:-7]}.csv"
        data.fs.load_from_disk(data_file_name=data_file_name, file_ext='csv',)
        self.assertFalse(data.ldf.empty)

    def test_cleanup_data_dir(self, *args, **kwargs):
        # Test cleanup of the data directory
        data = Data(name=self.name, fields_paths=[self.fields_path], data_dir=sts.test_data_dir)
        data.create_table()
        data.save_to_disk()
        max_files = 4
        data.fs.cleanup_data_dir(max_files=max_files)
        file_list = [f for f in os.listdir(data.fs.data_dir) if f.endswith('.csv')]
        self.assertLessEqual(len(file_list), max_files)

    def test_append(self, *args, **kwargs):
        # Test appending a new record to the DataFrame
        data = Data(name=self.name, fields_paths=[self.fields_path], data_dir=sts.test_data_dir)
        new_record = {
            'name': 'new_entry',
            'content': 'Some content',
            'prompt': 'Full prompt as posted to the model',
            'role': 'user',
            'category': 'test_category',
            'sub_category': 'test_sub_category',
            'source': 'https://www.example.com/...',
            'tools': 'ls -la',
            'hash': 'hash001',
            'model': 'test_model',
            'timestamp': pd.Timestamp.now()
        }
        data.append(new_record)
        self.assertIn('new_entry', data.ldf['name'].values)
        data.show(color=Fore.CYAN)

if __name__ == "__main__":
    unittest.main()
