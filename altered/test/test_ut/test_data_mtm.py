import os
import unittest
import time

# Assuming sts is correctly defined in altered.settings
import altered.settings as sts
from altered.data_mtm import Mtm  # Import Mtm class


class Test_Mtm(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 2
        cls.test_data_dir = sts.test_data_dir  # Assuming test_data_dir is set in settings
        cls.name = "Ut_Test_Mtm"
        cls.data_dir = sts.test_data_dir
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.num = 3
        cls.mtm = Mtm(name=cls.name, data_dir=cls.data_dir)  # Instantiate the Mtm class
        
    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    def test___init__(self, *args, **kwargs):
        """
        Test if the Mtm class initializes properly.
        """
        self.assertIsInstance(self.mtm, Mtm)
        self.mtm.show(verbose=2)
        print(self.mtm.columns.keys())

    # def test___call__(self, *args, **kwargs):
    #     # ws = Mtm(name=self.name, data_dir=self.data_dir)
    #     ws = Mtm(name=self.name, data_dir=self.data_dir)
    #     ws.results_to_table(verbose=self.verbose, max_files=6)
    #     ws.search_results.show(verbose=2)

if __name__ == "__main__":
    unittest.main()
