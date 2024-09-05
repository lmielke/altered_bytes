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
        cls.verbose = 0
        cls.testData = cls.mk_test_data(*args, **kwargs)
        cls.name = 'Unittest_Test_Data'

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        # Load test data from the YAML file
        file_path = os.path.join(sts.data_dir, 'default_fields.yml')
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)

    def test___init__(self, *args, **kwargs):
        # Test the initialization of the Data class
        data = Data(name=self.name, fields=self.testData)
        self.assertEqual(data.name, 'Unittest_Test_Data')

    def test_mk_data_dir(self, *args, **kwargs):
        # Test creation of the data directory
        data = Data(name=self.name, fields=self.testData)
        expected_dir = os.path.join(sts.data_dir, 'Unittest_Test_Data')
        self.assertTrue(os.path.exists(expected_dir))

    def test_load_fields(self, *args, **kwargs):
        # Test loading fields from YAML file
        data = Data(name=self.name)
        loaded_fields = data.load_fields(fields='default_fields.yml')
        self.assertEqual(loaded_fields, self.testData)

    def test_create_table(self, *args, **kwargs):
        # Test the creation of the DataFrame with the correct columns
        data = Data(name=self.name, fields=self.testData)
        data.create_table()
        self.assertFalse(getattr(data, self.name).empty)
        self.assertListEqual(list(getattr(data, self.name).columns), list(self.testData.keys()))

    def test_save_to_disk(self, *args, **kwargs):
        # Test saving the DataFrame to disk
        data = Data(name=self.name, fields=self.testData)
        data.create_table()
        data.save_to_disk()
        expected_file = f"{data.time_stamp.strftime(sts.time_strf)[:-7]}.csv"
        file_path = os.path.join(data.data_dir, expected_file)
        self.assertTrue(os.path.exists(file_path))

    def test_load_from_disk(self, *args, **kwargs):
        # Test loading the DataFrame from disk
        data = Data(name=self.name, fields=self.testData)
        data.create_table()
        data.save_to_disk()
        file_name = f"{data.time_stamp.strftime(sts.time_strf)[:-7]}.csv"
        data.load_from_disk(file_name=file_name)
        self.assertFalse(getattr(data, self.name).empty)

    def test_cleanup_data_dir(self, *args, **kwargs):
        # Test cleanup of the data directory
        data = Data(name=self.name, fields=self.testData)
        data.create_table()
        data.save_to_disk()
        data.cleanup_data_dir(max_entries=1)
        file_list = [f for f in os.listdir(data.data_dir) if f.endswith('.csv')]
        self.assertLessEqual(len(file_list), 1)

    def test_append(self, *args, **kwargs):
        # Test appending a new record to the DataFrame
        data = Data(name=self.name, fields=self.testData)
        new_record = {
            'name': 'new_entry',
            'unique_name': 'unique_001',
            'content': 'Some content',
            'prompt': 'Full prompt as posted to the model',
            'role': 'user',
            'category': 'test_category',
            'source': 'Some source',
            'tools': 'ls -la',
            'hash': 'hash001',
            'model': 'test_model',
            'timestamp': pd.Timestamp.now()
        }
        data.append(new_record)
        self.assertIn('new_entry', getattr(data, self.name)['name'].values)
        data.show(color=Fore.CYAN)

if __name__ == "__main__":
    unittest.main()
