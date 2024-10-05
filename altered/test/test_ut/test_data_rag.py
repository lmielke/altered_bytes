import os
import unittest
import time

# Assuming sts is correctly defined in altered.settings
import altered.settings as sts
from altered.data_rag import Rag  # Import Rag class


class Test_Rag(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 2
        cls.test_data_dir = sts.test_data_dir  # Assuming test_data_dir is set in settings
        cls.name = "Ut_Test_Rag"
        cls.data_dir = sts.test_data_dir
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.num = 3
        cls.rag = Rag(name=cls.name, data_file_name="memory", verbose=cls.verbose)
        
    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    def test___init__(self, *args, **kwargs):
        """
        Test if the Rag class initializes properly.
        """
        self.assertIsInstance(self.rag, Rag)
        self.rag.show(verbose=2)
        self.rag.save_vector_data(verbose=2, data_file_name="memory",)

    # def test___call__(self, *args, **kwargs):
    #     # ws = Rag(name=self.name, data_dir=self.data_dir)
    #     ws = Rag(name=self.name, data_dir=self.data_dir)
    #     ws.results_to_table(verbose=self.verbose, max_files=6)
    #     ws.search_results.show(verbose=2)

if __name__ == "__main__":
    unittest.main()
