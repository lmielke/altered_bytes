# test_prompt_user_prompt.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts

from altered.renderer import Render
from altered.prompt_user_prompt import UserPrompt

class Test_UserPrompt(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.renderer = Render(*args, **kwargs)

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
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test_get_prompt_str(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    # def test_get_user_prompt(self, *args, **kwargs):
    #     usr = UserPrompt(name='ut_test_prompt_user_prompt')
    #     user_prompt = usr.get_user_prompt(
    #                         prompt_str='Hello World!',
    #                         user_prompt=None,
    #         )
    #     print(f"test_get_user_prompt: \n{user_prompt = }")

    def test___call__(self, *args, **kwargs):
        usr2 = UserPrompt(name='ut_test_prompt_user_prompt')
        instructs = usr2(prompt_str="Why is the sky blue?", user_prompt='I have no idea.')
        rendered = self.renderer.render(
                                            template_name='user_prompt.md',
                                            context = {'instructs': instructs},
                                            verbose=self.verbose,
                                            )
        print(f"render result: \n{rendered}")


if __name__ == "__main__":
    unittest.main()
