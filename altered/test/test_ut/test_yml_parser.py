# test_labeled_data_frame.py
import json, os, re, shutil, sys, time, yaml
import unittest
# test package imports
import altered.settings as sts
from altered.yml_parser import YmlParser

class Test_YmlParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.test_data_path = os.path.join(sts.resources_dir, 'io', 'thought__thought_run.yml')
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

    def test___init__(self, *args, **kwargs):
        # Test initialization of YmlParser using fields from the YAML file
        yml_data = {field: [None] for field in self.test_data.keys()}
        yml = YmlParser(fields_paths=[self.test_data_path])

    def test_add_description(self, *args, **kwargs):
        # Create a DataFrame using the fields from the YAML file
        yml = YmlParser(fields_paths=[self.test_data_path])

        # Add descriptions
        yml.fields_text = ''
        yml.load_fields(fields_paths=[self.test_data_path])
        yml.add_labels(name='Unittest', description="Test DataFrame")

        # print(yml.describe(fmt='tbl'))
        print('\njson')
        print(yml.describe(fmt='json'))
        print('\nmarkdown')
        print(yml.describe(fmt='markdown'))
        print('\nyaml')
        print(yml.describe(fmt='yaml'))
        print(f"{yml.data = }")

if __name__ == "__main__":
    unittest.main()