# test_prompt.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.prompt import Prompt

class Test_Prompt(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.alias = 'l3.2_1'
        cls.verbose = 1
        cls.test_templates_names = ['agg_best']
        cls.test_io_template = 'simple_qa'
        cls.name = 'ut_Test_Prompt'
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        with open(os.path.join(sts.test_data_dir, 'test_thought_all_kwargs.yml'), 'r') as f:
            out = yaml.safe_load(f)
        return out

    def test___init__(self, *args, **kwargs):
        pr = Prompt(name='ut_Test_Prompt', *args, verbose=self.verbose, alias=self.alias)

    def test___call__(self, *args, **kwargs):
        prompt = Prompt(    name='ut_Test_Prompt', *args,
                            verbose=self.verbose, 
                            alias=self.alias)(**self.test_data, fmt='json', alias=self.alias)
        hlpp.pretty_prompt(prompt.data, *args, verbose=2, **kwargs)



if __name__ == "__main__":
    unittest.main()
