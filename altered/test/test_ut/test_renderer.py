# test_renderer.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from altered.renderer import Render

class Test_Render(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.context_path = os.path.join(sts.test_data_dir, "test_renderer.yml")
        cls.testData = cls.mk_test_data(*args, **kwargs)
        cls.inst = Render(*args, context_path=cls.context_path, **kwargs)
        print(f"Test_Render.inst.context: {cls.inst.context}")

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        with open(cls.context_path, "r") as f:
            out = yaml.safe_load(f)
        return out

    def test___init__(self, *args, **kwargs):
        self.assertEqual(
                            list(self.inst.context.keys()), 
                            ['prompt_title', 'context', 'user_prompt', 'instruct']
                            )

    def test_render(self, *args, **kwargs):
        rendered = self.inst.render(template_name='prompt.md', verbose=1,)
        print(rendered)

    def test_save_rendered(self, *args, **kwargs):

        self.inst.save_rendered(
                                    template_name='prompt.md', 
                                    output_file='test_renderer_Test_Render.md'
                                    )

if __name__ == "__main__":
    unittest.main()
