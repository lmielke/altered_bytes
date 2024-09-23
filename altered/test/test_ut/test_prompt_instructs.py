# test_prompt_instructs.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from altered.renderer import Render
from altered.prompt_instructs import Instructions

class Test_Instructions(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        # The idea being that there is always an instructs strategy and a output strategy
        cls.test_templates_names = ['agg_mean', 'qa_simple']
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
        inst = Instructions()

    def test___call__(self, *args, **kwargs):
        instr1 = Instructions()
        # test is using the qa template
        strats = instr1(  strat_templates=self.test_templates_names,
                        fmt='markdown',
                        user_prompt='Why do horses neigh?',
                        prompts=[
                                    'Why is the sky blue?',
                        ],
                        responses=[
                                    'The sky is blue because of Rayleigh scattering.',
                                    'There are 100 billion stars in the Milky Way galaxy.',
                                    'Airplanes fly because of Bernoullis...',
                        ],
                        )

        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name='instructs.md',
                                            context = {'instructs': strats},
                                            verbose=self.verbose,
                                            )
        print(f"render result: \n{rendered}")


if __name__ == "__main__":
    unittest.main()
