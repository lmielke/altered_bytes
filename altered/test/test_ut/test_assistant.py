# test_assistant.py

import os, re, shutil, sys, time, yaml
import unittest
from tabulate import tabulate as tb
# test package imports
import altered.settings as sts

from altered.model_connect import ModelConnect

class Test_Assistant(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.testData = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.test_inst = ModelConnect()

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        # with open(os.path.join(sts.test_data_dir, "someFile.yml"), "r") as f:
        #     out = yaml.safe_load(f)
        return out

    # def test___init__(self, *args, **kwargs):
    #     expected = False
    #     # initialize test class
    #     out = True
    #     # tests and asserts
    #     self.assertEqual(self.msg, expected)

    # def test_prep_context(self, *args, **kwargs):
    #     expected = False
    #     # initialize test class
    #     out = True
    #     # tests and asserts
    #     self.assertEqual(self.msg, expected)

    def test_post(self, *args, **kwargs):
        expected = False
        context = {'messages': [{'role': 'user', 'content': 'Why is the sky blue?'}]}
        # initialize test class
        outs= self.test_inst.post(
                                    [
                                    context['messages'][0]['content'],
                                    context['messages'][0]['content'],
                                    'Why is the sky not green?',
                                    ],
                                    alias='l3:8b_1',
                                    num_predict = 100,
                                    sub_domain='generates',
                                    agg_method='min',
                )
        # out = {k: f"{vs:12,d}" for k, vs in out.items() if k in ['load_duration', 'total_duration']}
        for i, out in enumerate(outs.get('results')):
            tbl = {k: f"{vs}"[:200] for k, vs in out.items()}
            print(tb(tbl.items()))

        # out = self.test_inst.generate(
        #                                 ['Why is the sky blue?'], 
        #                                 alias=('llama3.1', 'while-ai_1'),# as alias 'l3:8b_1',
        #                                 sub_domain='get_embeddings', # [get_embeddings, generate]
        #                                 )
        # print(out)
        # out = self.test_inst.generate(
        #                                 'Explain why the sky is blue!', 
        #                                 alias=('llama3.1', 'while-ai_1'),# as alias 'l3:8b_1',
        #                                 sub_domain='generate', # [get_embeddings, generate]
        #                                 )
        # print(out)
        # tests and asserts
        # self.assertEqual(self.msg, expected)

    # def test_while_ai(self, *args, **kwargs):
    #     expected = False
    #     # initialize test class
    #     out = True
    #     # tests and asserts
    #     self.assertEqual(self.msg, expected)

    # def test_openAI(self, *args, **kwargs):
    #     expected = False
    #     # initialize test class
    #     out = True
    #     # tests and asserts
    #     self.assertEqual(self.msg, expected)

if __name__ == "__main__":
    unittest.main()
