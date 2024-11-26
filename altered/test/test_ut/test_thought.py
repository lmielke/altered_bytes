# test_thought.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from altered.yml_parser import YmlParser
from colorama import Fore
import altered.hlp_printing as hlpp
from altered.thought import Thought


class Test_Thought(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 2
        cls.test_data_dir = sts.test_data_dir
        # cls.test_io_path = os.path.join(sts.test_data_dir, 'test_thought_denoise_text.yml')
        cls.test_io_path = os.path.join(sts.test_data_dir, 'test_thought_compress_text.yml')
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        # cls.thought = Thought(name='ut_chat')
        cls.thought = Thought(name='Test_Thought', verbose=cls.verbose)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        with open(cls.test_io_path, "r") as f:
            out = yaml.safe_load(f)
        return out

    def test___init__(self, *args, **kwargs):
        pass

    def test_run(self, *args, **kwargs):
        r = self.thought.think(*args, **self.test_data, verbose=self.verbose, r_filters=['response'])
        print(f"r: \n{r}")
        hlpp.pretty_prompt(r.get('response'), *args, verbose=self.verbose, **kwargs)


if __name__ == "__main__":
    unittest.main()
