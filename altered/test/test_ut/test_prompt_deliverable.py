# test_prompt_deliverable.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.renderer import Render
from altered.prompt_deliverable import Deliverable

class Test_Deliverable(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.test_data_path = os.path.join(sts.test_data_dir, "test_deliverable.py")
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.renderer = Render(*args, **kwargs)
        cls.delv = Deliverable()

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        with open(cls.test_data_path, "r") as f:
            out = f.read()
        return out

    def test_mk_context(self, *args, **kwargs):
        self.delv.mk_context(
                                            deliverable_path=self.test_data_path,
                                            deliverable=True,       
                                            )
        deliverable = {'deliverable': self.delv.context}
        # print(f"{deliverable = }")
        rendered = self.renderer.render(
                                            template_name=Deliverable.template_name,
                                            context = deliverable,
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)

if __name__ == "__main__":
    unittest.main()
