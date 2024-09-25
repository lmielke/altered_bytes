# test_prompt_strategies.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from colorama import Fore, Style

from altered.prompt_strategies import Strategy
from altered.prompt_strategies import Agg, Reduce
# we use renderer to veryfy the validity of results
from altered.renderer import Render


class Test_Strategy(unittest.TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.test_data_file_path = os.path.join(sts.io_dir, 'qa.yml')
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
        strat = Strategy()

    def test___call__(self, *args, **kwargs):
        agg2 = Agg()
        # test is using the qa template
        strats = agg2(  'agg_best', *args,
                        fmt='json',
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
        # for i, (k, v) in enumerate(strats.items()):
        #     print(f"\n{Fore.YELLOW}{i}{Fore.RESET} {k = }: {v}")
        # print(f"\n{strats['method']['inputs'] = }")
        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name='instructs_strats.md',
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        print(f"{Fore.GREEN}\nrender result multi:{Fore.RESET} \n{rendered}")



class Test_Agg(unittest.TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.test_data_file_path = os.path.join(sts.io_dir, 'qa.yml')
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
        strat = Agg()

    def test___call__(self, *args, **kwargs):
        agg3 = Agg()
        # test is using the qa template
        strats = agg3(  'agg_best', *args,
                        fmt='json',
                        prompts=[
                                    'Why is the sky blue?',
                                    'How many stars are in the sky?',
                                    'How do airplanes fly?',
                        ][:1],
                        responses=[
                                    'The sky is blue because of Rayleigh scattering.',
                                    'There are 100 billion stars in the Milky Way galaxy.',
                                    'Airplanes fly because of Bernoullis...',
                        ],
                        )
        # for i, (k, v) in enumerate(strats.items()):
        #     print(f"\n{Fore.YELLOW}{i}{Fore.RESET} {k = }: {v}")
        # print(f"\n{strats['method']['inputs'] = }")
        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name='instructs_strats.md',
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        print(f"{Fore.CYAN}\nrender result single:{Fore.RESET} \n{rendered}")

        agg4 = Agg()
        # test is using the qa template
        strats = agg4(  'agg_best', *args,
                        fmt='json',
                        prompts=[],
                        responses=[
                                    'The sky is blue because of Rayleigh scattering.',
                                    'There are 100 billion stars in the Milky Way galaxy.',
                                    'Airplanes fly because of Bernoullis...',
                        ],
                        )
        # for i, (k, v) in enumerate(strats.items()):
        #     print(f"\n{Fore.YELLOW}{i}{Fore.RESET} {k = }: {v}")
        # print(f"\n{strats['method']['inputs'] = }")
        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name='instructs_strats.md',
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        print(f"{Fore.BLUE}\nrender result None:{Fore.RESET} \n{rendered}")


class Test_Reduce(unittest.TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.test_data_file_path = os.path.join(sts.io_dir, 'qa.yml')
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

    def test___call__(self, *args, **kwargs):
        reduce_1 = Reduce()
        # test is using the qa template
        strats = reduce_1(  'reduce_text', *args,
                        fmt='json',
                        prompts=[],
                        responses=[
                                    'The sky is blue because of Rayleigh scattering.',
                        ],
                        )
        # for i, (k, v) in enumerate(strats.items()):
        #     print(f"\n{Fore.YELLOW}{i}{Fore.RESET} {k = }: {v}")
        # print(f"\n{strats['method']['inputs'] = }")
        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name='instructs_strats.md',
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        print(f"{Fore.RED}\nrender result None:{Fore.RESET} \n{rendered}")


if __name__ == "__main__":
    unittest.main()
