# test_prompt_instructs.py

import os, re, shutil, sys, time, yaml
import unittest
from colorama import Fore, Style
import altered.hlp_printing as hlpp

# test package imports
import altered.settings as sts
from altered.renderer import Render
from altered.prompt_instructs import Instructions

class Test_Instructions(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        # The idea being that there is always an instructs strategy and a output strategy
        cls.test_templates_names = ['agg_mean']
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
        inst = Instructions(name='Test_Instructions')

    def test___call__(self, *args, **kwargs):
        instr1 = Instructions(name='Test_Instructions')
        # test is using the qa template
        strats = instr1(  
                        strat_template='agg_mean',
                        io_template='simple_qa',
                        fmt='json',
                        max_files=6,
                        prompts=[
                                    'Why is the sky blue?',
                                    'How many stars are in the sky?',
                                    'How do airplanes fly?',
                        ],
                        responses=[
                                    'The sky is blue because of Rayleigh scattering.',
                                    'There are 100 billion stars in the Milky Way galaxy.',
                                    'Airplanes fly because of Bernoullis...',
                        ],
                        )
        # for i, (k, v) in enumerate(strats.context.items()):
        #     print(f"\n{Fore.YELLOW}{i}{Fore.RESET} {k = }: {v}")

        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name=Instructions.template_name,
                                            context = {'instructs': strats.context},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)


        with open(os.path.join(sts.test_data_dir, 'test_search_engine_cleaned.yml'), 'r') as f:
            out = yaml.safe_load(f)

        instr2 = Instructions(name='Test_Instructions')
        # test is using the qa template
        strats = instr2(strat_template='clean_text',
                        io_template='simple_qa',
                        # user_prompt='Why do horses neigh?',
                        user_prompt=out.get('user_prompt'),
                        search_query=out.get('search_query'),
                        strat_input_data=out.get('content'),
                        )

        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name=Instructions.template_name,
                                            context = {'instructs': strats.context},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)


if __name__ == "__main__":
    unittest.main()
