import os
import unittest
import time

# Assuming sts is correctly defined in altered.settings
import altered.settings as sts
from altered.data_stm import Stm  # Import Stm class


class Test_Stm(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 2
        cls.test_data_dir = sts.test_data_dir  # Assuming test_data_dir is set in settings
        cls.name = "Ut_Test_Stm"
        cls.data_dir = sts.test_data_dir
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.num = 3
        cls.stm = Stm(name=cls.name, data_dir=cls.data_dir)  # Instantiate the Stm class
        
    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    def test___init__(self, *args, **kwargs):
        """
        Test if the Stm class initializes properly.
        """
        self.assertIsInstance(self.stm, Stm)
        self.stm.show(verbose=2)
        print(self.stm.columns.keys())

    # def test___call__(self, *args, **kwargs):
    #     # ws = Stm(name=self.name, data_dir=self.data_dir)
    #     ws = Stm(name=self.name, data_dir=self.data_dir)
    #     ws.results_to_table(verbose=self.verbose, max_files=6)
    #     ws.search_results.show(verbose=2)

if __name__ == "__main__":
    unittest.main()
