# test_prompt_context_sys_info.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.renderer import Render
from altered.prompt_context_sys_info import ContextSysInfo

class Test_ContextSysInfo(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.test_io_path = os.path.join(sts.test_data_dir, 'test_prompt_context_sys_info_kwargs.yml')
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.renderer = Render(*args, **kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass
    
    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        with open(cls.test_io_path, "r") as f:
            out = yaml.safe_load(f)
        return out

    def test_mk_context(self, *args, **kwargs):
        cont = ContextSysInfo()
        context = cont.mk_context(**self.test_data)
        print(f"test_mk_context.context: {context}")
        rendered = self.renderer.render(
                                            template_name=ContextSysInfo.template_name,
                                            context = {'context': context},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)

if __name__ == "__main__":
    unittest.main()
