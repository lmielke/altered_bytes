import os
import unittest
from colorama import Fore, Style

from altered.yml_parser import YmlParser
import altered.settings as sts
from altered.chat_vec import VecChat
VecChat.chats_dir = os.path.join(sts.test_data_dir, 'thoughts')

verbose = 1

class Test_VecChat(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
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
        v_chat = VecChat(name='ut_v_chat')
        print(v_chat.data.show())
        print(f"{v_chat.data.fields = }")

    def test_run(self, *args, **kwargs):
        print(f"{Fore.RED}test_run: {Fore.RESET}{verbose = }")
        v_chat = VecChat(name='ut_v_chat', verbose=verbose)
        # we use YmlParser here to load the test_data kwargs from a YAML file
        yml = YmlParser()
        yml.add_labels(name='Unittest', labels=self.test_data_path, description="run v_chat")
        yml.data['verbose'] = verbose
        yml.data['fmt'] = 'json'
        v_chat.run(*args, **yml.data, 
                    example=os.path.join(self.test_data_dir, 'strategies', 'simple_answer.yml'))
