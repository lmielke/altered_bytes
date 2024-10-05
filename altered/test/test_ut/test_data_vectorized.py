# test_data_vectorized.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from colorama import Fore, Style

from altered.data_vectorized import VecDB

class Test_VecDB(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.test_file_name = 'test_memory_data_load_fields.yml'
        cls.fields_path = os.path.join(sts.test_data_dir, cls.test_file_name)
        cls.test_data_path = os.path.join(sts.test_data_dir, cls.test_file_name)
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.name = 'UT_Test_VecDB'
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.d_vec = VecDB(
                                name=cls.name,
                                u_fields_paths=[cls.fields_path,],
                                data_dir=sts.test_data_dir,
                                verbose=cls.verbose,
                                )

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        # Load test data from the YAML file
        with open(cls.test_data_path, 'r') as f:
            return yaml.safe_load(f)

    def test___init__(self, *args, **kwargs):
        # Test the initialization of the VecDB class
        self.assertEqual(self.d_vec.name, self.name)

    def test_append(self, *args, **kwargs):
        content = 'test_data_vectorized.Test_VecDB.test_append'
        # append the content at the last postion in the data_vectorized table
        self.d_vec.append({'role': 'user', 'content': content})
        last_memory = self.d_vec.ldf.loc[self.d_vec.hashify(self.d_vec.vectors[1, 1])]
        self.assertEqual(content, last_memory['content'])

    def test_get(self, *args, **kwargs):
        # Prepare test entries for data_vectorized
        test_contents = [
                            'What is the capital of France?',
                            'How does a plane fly?',
                            'Why is the sky blue?',
                            'What is the meaning of life?',
                            'What causes earthquakes?',
                            'How do computers work?',
                            'Explain the theory of relativity.',
                            'What is quantum mechanics?',
                            'How do magnets work?',
                            'Why do we dream?',
        ]
        
        # Add these entries to data_vectorized
        for entry in test_contents:
            self.d_vec.append({'role': 'user', 'content': entry},)
        self.d_vec.show(verbose=2)
        # Query that is nearest to one of the test entries
        query = "Why is the sky blue?"
        # Retrieve similar entries
        nearests = self.d_vec.get(query, num=5, verbose=self.verbose)
        self.assertEqual(nearests['records'][0]['content'], 'Why is the sky blue?')

    def test_save_vector_data(self, *args, **kwargs):
        test_contents = [
                            'What is the capital of France?',
                            'How does a plane fly?',
                            'Why is the sky blue?',
        ]
        # Add these entries to data_vectorized
        for entry in test_contents:
            self.d_vec.append({'role': 'user', 'content': entry})
        self.d_vec.save_to_disk(max_files=4, verbose=self.verbose)

    def test_load_vector_data(self, *args, **kwargs):
        time.sleep(2)
        
        self.d_vec.load_from_disk( *args, verbose=self.verbose, **kwargs, )

        self.d_vec.show(verbose=2)


if __name__ == "__main__":
    unittest.main()
