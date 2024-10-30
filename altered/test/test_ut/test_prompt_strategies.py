# test_prompt_strategies.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from colorama import Fore, Style
import altered.hlp_printing as hlpp
from altered.prompt_strategies import Strategy
from altered.prompt_strategies import Agg, Denoise, Denoisetext
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
        strats = agg2(  'agg_mean', *args,
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
        # for i, (k, v) in enumerate(strats.items()):
        #     print(f"\n{Fore.YELLOW}{i}{Fore.RESET} {k = }: {v}")
        # print(f"\n{strats['method']['inputs'] = }")
        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name=Strategy.template_name,
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)



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
        strats = agg3(  'agg_mean', *args,
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
                                            template_name=Strategy.template_name,
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)

        agg4 = Agg()
        # test is using the qa template
        strats = agg4(  'agg_mean', *args,
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
                                            template_name=Strategy.template_name,
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)

        agg5 = Agg()
        # test is using the qa template
        strats = agg5(  'agg_std', *args,
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
                                            template_name=Strategy.template_name,
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)


class Test_Denoise(unittest.TestCase):

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
        reduce_1 = Denoise()
        # test is using the qa template
        strats = reduce_1(  'denoise_text', *args,
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
                                            template_name=Strategy.template_name,
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)

class Test_DenoiseText(unittest.TestCase):

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
        with open(os.path.join(sts.test_data_dir, "test_prompt_strategies_denoise_text.yml"), "r") as f:
            out = yaml.safe_load(f)
        return out

    def test___call__(self, *args, **kwargs):
        denoise_1 = Denoisetext()
        # test is using the qa template
        strats = denoise_1(  'denoisetext_text', *args,
                        fmt='json',
                        text=self.test_data['text_0'],
                        )
        # for i, (k, v) in enumerate(strats.items()):
        #     print(f"\n{Fore.YELLOW}{i}{Fore.RESET} {k = }: {v}")
        # print(f"\n{strats['method']['inputs'] = }")
        # here we give the output of the __call__ test to renderer to veryfy the correctness
        rendered = self.renderer.render(
                                            template_name=Strategy.template_name,
                                            context = {'instructs': {'strats': strats}},
                                            verbose=self.verbose,
                                            )
        hlpp.pretty_prompt(rendered, *args, verbose=2, **kwargs)


if __name__ == "__main__":
    unittest.main()
