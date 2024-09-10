# test_chat.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from altered.yml_parser import YmlParser

from altered.chat import Chat

class Test_Chat(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.test_data_path = os.path.join(sts.resources_dir, 'kwargs', 'chat_run.yml')
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
        chat = Chat(name='ut_chat', verbose=self.verbose)
        # chat.table().fields.describe(fmt='tbl')
        yml = YmlParser()
        yml.add_labels(name='Unittest', labels=self.test_data_path, description="run chat")
        yml.data['verbose'] = self.verbose
        chat.run(*args, **yml.data)


if __name__ == "__main__":
    unittest.main()
