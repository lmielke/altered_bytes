# test_prompt_instructs.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts

from altered.prompt_instructs import Instructions

class Test_Instructions(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.test_data_dir = os.path.join(sts.resources_dir, 'kwargs')
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.inst = Instructions()

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        # with open(os.path.join(sts.test_data_dir, "someFile.yml"), "r") as f:
        #     out = yaml.safe_load(f)
        return out

    def test___init__(self, *args, **kwargs):
        self.assertIn('json', self.inst.instructs_fmts.keys())

    # def test_user_prompt(self, *args, **kwargs):
    #     expected = False
    #     # initialize test class
    #     out = True
    #     # tests and asserts
    #     self.assertEqual(self.msg, expected)

    # def test_data(self, *args, **kwargs):
    #     expected = False
    #     # initialize test class
    #     out = True
    #     # tests and asserts
    #     self.assertEqual(self.msg, expected)

    # def test_get_user_prompt(self, *args, **kwargs):
    #     expected = False
    #     # initialize test class
    #     out = True
    #     # tests and asserts
    #     self.assertEqual(self.msg, expected)

    def test_create_instruct_dict(self, *args, **kwargs):
        data = self.inst.create_instruct_dict(   user_prompt='Hello World', 
                                            instructs='Follow the white rabbit!'
                )
        print(f"{self.inst._data = }")

    def test_get_response_template(self, *args, **kwargs):
        data = self.inst.get_response_template(example=os.path.join(
                                                                self.test_data_dir, 
                                                                'thought__thought_run.yml'),
                                                fmt='json'
                )
        print(f"{data = }")

    def test_set_response_format(self, *args, **kwargs):
        data = self.inst.get_response_template(example=os.path.join(
                                                                self.test_data_dir, 
                                                                'thought__thought_run.yml'),
                                                fmt='json'
                )
        self.inst.set_response_format(data, fmt='json')
        print(f"self.inst._data: {self.inst._data}")

    def test_get_strategy(self, *args, **kwargs):
        strategy = self.inst.get_strategy(strategy = 'prompt_aggregations')
        print(f"\n{strategy = }\n")
        strategy = self.inst.get_strategy(strategy = 'prompt_aggregations.max')
        print(f"\nmax: {strategy = }\n")

    # def test_load_prompt_params(self, *args, **kwargs):
    #     expected = False
    #     # initialize test class
    #     out = True
    #     # tests and asserts
    #     self.assertEqual(self.msg, expected)

if __name__ == "__main__":
    unittest.main()
