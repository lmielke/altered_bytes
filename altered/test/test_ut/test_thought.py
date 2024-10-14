# test_thoughts.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from altered.yml_parser import YmlParser
from colorama import Fore
from altered.thought import Thought

verbose = 3

class Test_Thought(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.test_data_dir = sts.test_data_dir
        cls.test_io_path = os.path.join(sts.resources_dir, 'io', 'thought__thought_run.yml')
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        # cls.thought = Thought(name='ut_chat')
        cls.thought = Thought(name='Test_Thought', verbose=verbose)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        yml = YmlParser(fields_paths=[cls.test_io_path])
        yml.add_labels(name='Test_Thought', labels=cls.test_io_path, description="run thought")
        return yml.data

    def test___init__(self, *args, **kwargs):
        pass

    def test_run(self, *args, **kwargs):
        # we use YmlParser here to load the test_data kwargs from a YAML file
        r = self.thought.think(*args, **self.test_data, r_filters=['response'])
        print(f"r: \n{r}")


if __name__ == "__main__":
    unittest.main()
