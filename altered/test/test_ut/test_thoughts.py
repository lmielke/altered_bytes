# test_thoughts.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from altered.yml_parser import YmlParser
from colorama import Fore
from altered.thoughts import Thoughts
Thoughts.thoughts_dir = os.path.join(sts.test_data_dir, 'thoughts')


class Test_Thoughts(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 3
        cls.test_data_dir = sts.test_data_dir
        cls.test_io_path = os.path.join(sts.resources_dir, 'io', 'thought__thought_run.yml')
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        # cls.thoughts = Thoughts(name='ut_thought')
        cls.thoughts = Thoughts(name='ut_thought', verbose=cls.verbose, 
                                                                data_dir=cls.test_data_dir)

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
        self.thoughts.run(*args, **self.test_data, max_files=6)


if __name__ == "__main__":
    unittest.main()
