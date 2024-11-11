# test_prompt_strategies.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from colorama import Fore, Style
import altered.hlp_printing as hlpp
from altered.prompt_strategies import Strategy
from altered.prompt_strategies import Agg, Format, Clean
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
        strats, fmt = agg2(*args,
                        params={'method': 'agg', 't_name': 'agg_mean', 'sub_method': 'mean'},
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
        strats, fmt = agg3(*args,
                        params={'method': 'agg', 't_name': 'agg_max', 'sub_method': 'max'},
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
        strats, fmt = agg4(*args,
                        params={'method': 'agg', 't_name': 'agg_min', 'sub_method': 'min'},
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
        # test is using NO io_template, because this only tests the strat_template
        # therefore the prompt Response Layout section will recomment markdown (no prob)
        strats, fmt = agg5(*args,
                        params={'method': 'agg', 't_name': 'agg_std', 'sub_method': 'std'},
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

        agg6 = Agg()
        # test is using NO io_template, because this only tests the strat_template
        # therefore the prompt Response Layout section will recomment markdown (no prob)
        strats, fmt = agg6(*args,
                        params={'method': 'agg', 't_name': 'agg_best', 'sub_method': 'best'},
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


class Test_Format(unittest.TestCase):

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
        reduce_1 = Format()
        # test is using the qa template
        strats, fmt = reduce_1(*args,
                        params={'method': 'format', 't_name': 'format_short', 'sub_method': 'short'},
                        fmt='json',
                        prompts=[],
                        strat_input_data = 'The sky is blue because of Rayleigh scattering.',
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

class Test_Clean(unittest.TestCase):

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
        with open(os.path.join(sts.test_data_dir, "test_prompt_strategies_denoise_text.yml"), 
                    "r", encoding="utf-8") as f:
            out = yaml.safe_load(f)
        return out

    def test___call__(self, *args, **kwargs):
        denoise_1 = Clean()
        # test is using the qa template
        strats, fmt = denoise_1( *args,
                        params={'method': 'clean', 't_name': 'clean_text', 'sub_method': 'text'},
                        fmt='json',
                        strat_input_data=self.test_data['text_0'],
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
