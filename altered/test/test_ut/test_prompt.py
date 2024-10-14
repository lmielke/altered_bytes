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
                    'user_prompt': 'I am having trouble with my list comprehensions?',
                    'sys_info': True,
                    'num_activities': 3,
                    'package_infos': True,
                    'root_file_name': 'prompt_instructs.py',
                    'file_match_regex': 'settings.*',
                    'chat_history': [
                            {'role': 'user', 'content': 'What are list comprehensions?'},
                            {'role': 'assistant', 'content': 'List comprehensions are a way to create lists in Python.'},
                            {'role': 'user', 'content': 'I need these with Python programming.'},
                            {'role': 'assistant', 'content': 'Sure, I can help you with that.'},
                        ],
                    'init_prompt': {'role': 'user', 'content': 'What are list comprehensions?'},
                    'strat_templates': self.test_templates_names,
                    # 'io_template': self.test_io_template,
                    'prompts': [
                                'What are list comprehensions?',
                                'What use have list comprehensions?',
                                'Why do we need list comprehensions?',
                    ],
                    'responses': [
                                'List comprehensions are single line list creation methods.',
                                'List comprehensions provide a way to create complex lists.',
                                'You can create lists in Python using list comprehensions.',
                    ],
                    'search_results': [
                                        {'source': 'https://www.stackoverflow.com/some_topic', 'content': 'Search Query is None because this is unittest'},
                                        {'source': 'https://www.stackexchange.com/some_other_topic', 'content': 'List comprehensions in Python'},
                                        {'source': 'https://www.python.org/some_topic', 'content': 'Python list comprehensions'},
                    ],
                    'search_query': 'list comprehensions in Python',
                    }
        prompt = Prompt(name='ut_Test_Prompt', *args, verbose=self.verbose, alias=self.alias)(**_context, fmt='json', alias=self.alias)
        hlpp.pretty_prompt(prompt.data, *args, verbose=2, **kwargs)



if __name__ == "__main__":
    unittest.main()
