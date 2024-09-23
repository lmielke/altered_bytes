# test_thoughts.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from altered.yml_parser import YmlParser
from colorama import Fore
from altered.thoughts import Chat
Chat.chats_dir = os.path.join(sts.test_data_dir, 'thoughts')

verbose = 2

class Test_Chat(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.test_data_dir = sts.resources_dir
        cls.test_data_path = os.path.join(cls.test_data_dir, 'io', 'thought__thought_run.yml')
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
        print(f"{chat.data.fields = }")

    def test_run(self, *args, **kwargs):
        chat = Chat(name='ut_chat', verbose=verbose)
        # we use YmlParser here to load the test_data kwargs from a YAML file
        print(f"{self.test_data_path = }")
        yml = YmlParser(fields_paths=[self.test_data_path])
        yml.add_labels(name='Unittest', labels=self.test_data_path, description="run chat")
        yml.data['verbose'] = verbose
        yml.data['fmt'] = 'json'
        del yml.data['fmt']
        chat.run(*args, **yml.data, repeats=3,)


if __name__ == "__main__":
    unittest.main()
