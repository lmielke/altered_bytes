# test_prompt.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.prompt import Prompt

class Test_Prompt(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.alias = 'l3.2_1'
        cls.verbose = 1
        cls.test_templates_names = ['agg_best']
        cls.test_io_template = 'simple_qa'
        cls.name = 'ut_Test_Prompt'
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '

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
        pr = Prompt(name='ut_Test_Prompt', *args, verbose=self.verbose, alias=self.alias)

    def test___call__(self, *args, **kwargs):
        _context = {
                    # 'search_query': 'list comprehensions in Python',
                    # 'strategy': 'prompt_aggregations.mean',
                    # 'search_results': [
                    #                     {'source': 'https://www.stackoverflow.com/some_topic', 'content': 'Search Query is None because this is unittest'},
                    #                     {'source': 'https://www.stackexchange.com/some_other_topic', 'content': 'List comprehensions in Python'},
                    #                     {'source': 'https://www.python.org/some_topic', 'content': 'Python list comprehensions'},
                    # ],
                    'num_activities': 3,
                    'activities': True,
                    'sys_info': True,
                    'package_infos': True,
                    'root_file_name': 'prompt_instructs.py',
                    'file_match_regex': 'settings.*',
                    'chat_history': [
                            {'role': 'user', 'content': 'Hello, how can you help me today?'},
                            {'role': 'assistant', 'content': 'Id be happy to assist you. What kind of help do you need?'},
                            {'role': 'user', 'content': 'I need help with Python programming.'},
                            {'role': 'assistant', 'content': 'Sure, I can help with Python. What specific aspect are you working on?'},
                            {'role': 'user', 'content': 'I am having trouble with list comprehensions.'}
                        ],
                    'init_prompt': {'role': 'user', 'content': 'Hello, how can you help me today?'},
                    'name': self.name,
                    'strat_templates': self.test_templates_names,
                    'io_template': self.test_io_template,
                    'user_prompt': 'Why is the sky blue?',
                    'prompts': [
                                'Why is the sky blue?',
                                'How many stars are in the sky?',
                                'How do airplanes fly?',
                    ],
                    'responses': [
                                'The sky is blue because of Rayleigh scattering.',
                                'There are 100 billion stars in the Milky Way galaxy.',
                                'Airplanes fly because of Bernoullis...',
                    ],
                    'verbose': self.verbose,
                    }
        prompt = Prompt(name='ut_Test_Prompt', *args, verbose=self.verbose, alias=self.alias)(**_context, fmt='json', alias=self.alias)
        hlpp.pretty_prompt(prompt.data, *args, verbose=2, **kwargs)



if __name__ == "__main__":
    unittest.main()
