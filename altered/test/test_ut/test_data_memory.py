import os
import unittest
import time

# Assuming sts is correctly defined in altered.settings
import altered.settings as sts
from altered.data_memory import Memory  # Import Memory class


class Test_Memory(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 2
        cls.test_data_dir = sts.test_data_dir  # Assuming test_data_dir is set in settings
        cls.name = "Ut_Test_Memory"
        cls.data_dir = sts.test_data_dir
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '
        cls.num = 3
        cls.memory = Memory(
                            name=cls.name, 
                            data_file_name="memory", 
                            data_dir=cls.data_dir, 
                            verbose=cls.verbose
                            )
        
    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    def test___init__(self, *args, **kwargs):
        """
        Test if the Memory class initializes properly.
        """
        self.assertIsInstance(self.memory, Memory)
        self.memory.show(verbose=2)
        self.memory.save_to_disk(verbose=self.verbose, max_files=4, data_file_name="memory",)

    def test_find_memories(self, *args, **kwargs):
        memories = self.memory.find_memories(memory_dir=self.data_dir)
        print(f"test_data_memory: {memories = }")
        print(f"test_data_memory: {self.memory.columns.keys()}")

    def test_load_memories(self, *args, **kwargs):
        memories = self.memory.find_memories(memory_dir=self.data_dir)
        self.memory.load_memories(memories)

if __name__ == "__main__":
    unittest.main()
