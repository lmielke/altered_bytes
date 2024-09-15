# test_thoughts.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from altered.yml_parser import YmlParser

from altered.thoughts import Chat
Chat.chats_dir = os.path.join(sts.test_data_dir, 'thoughts')

class Test_Chat(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.test_data_dir = os.path.join(sts.resources_dir,)
        cls.test_data_path = os.path.join(cls.test_data_dir, 'kwargs', 'thought__thought_run.yml')
        cls.test_data = cls.mk_test_data(*args, **kwargs)
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
        # we use YmlParser here to load the test_data kwargs from a YAML file
        yml = YmlParser()
        yml.add_labels(name='Unittest', labels=self.test_data_path, description="run chat")
        yml.data['verbose'] = self.verbose
        yml.data['fmt'] = 'json'
        chat.run(*args, **yml.data, 
                    example=os.path.join(self.test_data_dir, 'strategies', 'simple_answer.yml'))


if __name__ == "__main__":
    unittest.main()
