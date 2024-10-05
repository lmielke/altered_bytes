# test_prompt_io.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from colorama import Fore, Style
import altered.hlp_printing as hlpp
from altered.prompt_io import Io, Simple
# we use renderer to veryfy the validity of results
from altered.renderer import Render


class Test_Strategy(unittest.TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.test_data = cls.mk_test_data(*args, **kwargs)
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
        io_inst = Simple()
        io = io_inst(  'simple_qa', *args, fmt='json', max_files=6, )
        # for i, (k, v) in enumerate(io.items()):
        #     print(f"\n{Fore.YELLOW}{i}{Fore.RESET} {k = }: {v}")
        # print(f"\n{io['method'] = }")
        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name=Io.template_name,
                                            context = {'instructs': {'io': io}},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)


if __name__ == "__main__":
    unittest.main()
