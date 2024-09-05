# test_chat.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts

from altered.chat import Chat

class Test_Chat(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 2
        cls.testData = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '

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
        chat = Chat(name='ut_chat')
        print(chat.data.show())

    def test_run(self, *args, **kwargs):
        chat = Chat(name='ut_chat')
        chat.run('Hello, Who are you?', *args, 
                        verbose=0, 
                        alias='l3:8b_1',
                        num_predict = 100,
                        depth=1, 
                        **kwargs
        )

if __name__ == "__main__":
    unittest.main()
