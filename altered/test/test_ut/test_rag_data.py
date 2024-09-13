# test_rag_data.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
from colorama import Fore, Style

from altered.rag_data import RAG_DB

class Test_Memory(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.test_data_path = os.path.join(sts.test_data_dir, 'test_memory_data_load_fields.yml')
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.name = 'Unittest_Test_Memory'
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.rag_data = RAG_DB(
                                name=cls.name,
                                fields=cls.test_data,
                                data_dir=os.path.join(sts.test_data_dir, cls.name),
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
        # Test the initialization of the RAG_DB class
        self.assertEqual(self.rag_data.name, 'Unittest_Test_Memory')

    def test_setup_storage(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test_hashify(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test_embedd(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test_update_vector_store(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test_normalize(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test_append(self, *args, **kwargs):
        content = 'test_rag_data.Test_Memory.test_append'
        # append the content at the last postion in the rag_data table
        self.rag_data.append({'role': 'user', 'content': content})
        last_memory = self.rag_data.m_data.loc[self.rag_data.hashify(self.rag_data.vectors[-1, 1])]
        self.assertEqual(content, last_memory['content'])

    def test_get(self, *args, **kwargs):
        # Prepare test entries for rag_data
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
        
        # Add these entries to rag_data
        for entry in test_contents:
            self.rag_data.append({'role': 'user', 'content': entry})
        self.rag_data.show()
        # Query that is nearest to one of the test entries
        query = "Why is the sky blue?"
        # Retrieve similar entries
        nearests = self.rag_data.get(query, num=5, verbose=self.verbose)
        self.assertEqual(nearests['records'][0]['content'], 'Why is the sky blue?')

    def test_save_to_disk(self, *args, **kwargs):
        test_contents = [
                            'What is the capital of France?',
                            'How does a plane fly?',
                            'Why is the sky blue?',
        ]
        # Add these entries to rag_data
        for entry in test_contents:
            self.rag_data.append({'role': 'user', 'content': entry})
        self.rag_data.save_to_disk(max_files=4, verbose=self.verbose)

    def test_load_from_disk(self, *args, **kwargs):
        time.sleep(2)
        self.rag_data.load_from_disk( *args,
                                    data_file_name='latest',
                                    verbose=self.verbose,
                                    **kwargs,
                                    )
        self.rag_data.show()

    def test_get_stats(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test_compare(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test_find_nearest(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test___str__(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

    def test_explain(self, *args, **kwargs):
        expected = False
        # initialize test class
        out = True
        # tests and asserts
        self.assertEqual(self.msg, expected)

if __name__ == "__main__":
    unittest.main()
