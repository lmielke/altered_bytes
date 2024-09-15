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
        cls.test_data_dir = os.path.join(sts.data_dir, 'data__data_load_fields_default.yml')
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.name = 'Unittest_Test_Data'

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        # Load test data from the YAML file
        with open(cls.test_data_dir, 'r') as f:
            return yaml.safe_load(f)

    def test___init__(self, *args, **kwargs):
        # Test the initialization of the Data class
        data = Data(name=self.name, fields=self.test_data)
        self.assertEqual(data.name, 'Unittest_Test_Data')

    def test_mk_data_dir(self, *args, **kwargs):
        # Test creation of the data directory
        data = Data(name=self.name, fields=self.test_data)
        expected_dir = os.path.join(sts.data_dir, 'Unittest_Test_Data')
        self.assertTrue(os.path.exists(expected_dir))

    def test_load_fields(self, *args, **kwargs):
        # Test loading fields from YAML file
        data = Data(name=self.name)
        loaded_fields = data.load_fields(fields='data__data_load_fields_default.yml')
        self.assertEqual(loaded_fields, self.test_data)

    def test_create_table(self, *args, **kwargs):
        # Test the creation of the DataFrame with the correct columns
        data = Data(name=self.name, fields=self.test_data)
        data.create_table()
        self.assertFalse(data.ldf.empty)
        self.assertListEqual(list(data.ldf.columns), list(self.test_data.keys()))

    def test_save_to_disk(self, *args, **kwargs):
        # Test saving the DataFrame to disk
        data = Data(name=self.name, fields=self.test_data)
        data.create_table()
        data.save_to_disk()
        expected_file = f"{data.time_stamp.strftime(sts.time_strf)[:-7]}.csv"
        file_path = os.path.join(data.data_dir, expected_file)
        self.assertTrue(os.path.exists(file_path))

    def test_load_from_disk(self, *args, **kwargs):
        # Test loading the DataFrame from disk
        data = Data(name=self.name, fields=self.test_data)
        data.create_table()
        data.save_to_disk()
        data_file_name = f"{data.time_stamp.strftime(sts.time_strf)[:-7]}.csv"
        data.load_from_disk(data_file_name=data_file_name)
        self.assertFalse(data.ldf.empty)

    def test_cleanup_data_dir(self, *args, **kwargs):
        # Test cleanup of the data directory
        data = Data(name=self.name, fields=self.test_data)
        data.create_table()
        data.save_to_disk()
        data.cleanup_data_dir(max_files=1)
        file_list = [f for f in os.listdir(data.data_dir) if f.endswith('.csv')]
        self.assertLessEqual(len(file_list), 1)

    def test_append(self, *args, **kwargs):
        # Test appending a new record to the DataFrame
        data = Data(name=self.name, fields=self.test_data)
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
