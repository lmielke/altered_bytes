# test_deep_thought.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts

from altered.rag_thought import RAG_Thought
RAG_Thought.thoughts_dir = sts.test_data_dir

class Test_RAG_Thought(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.test_name = 'Test_Deep_Thought'
        cls.verbose = 0
        cls.test_data_dir = os.path.join(sts.test_data_dir, cls.test_name)
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.rag = RAG_Thought(*args, name=cls.test_name, **kwargs)

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
        self.assertEqual(self.rag.name, self.test_name.lower())

    def test___call__(self, *args, **kwargs):
        self.rag((
                        f"How can I monitor my nvidia GPU performance on Windows 10"
                        f" using powershell?"
                        ), *args,
                        fmt='json', 
                        temperature=0.1, 
                        **kwargs,
        )

if __name__ == "__main__":
    unittest.main()
