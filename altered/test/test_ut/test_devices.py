import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.devices import Devices

from altered.prompt_tool_choice import FunctionToJson


class Test_Devices(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.test_data = cls.mk_test_data(*args, **kwargs)
        cls.msg = f' >>>> NOT IMPLEMENTED <<<< '

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        out = None
        return out

    @FunctionToJson(schemas={"openai"}, write=True)
    def test_toggle_device(self, *args, **kwargs):
        expected = False
        out = True
        # --- MINIMAL ADJUSTMENT HERE ---
        # Change 'device_name' to 'room' and 'name' as keyword arguments
        # Pass *args and **kwargs through as they were in the original call
        Devices.toggle_device(*args, room="office", name="panel_led_lamp", **kwargs)
        # --- END MINIMAL ADJUSTMENT ---
        self.assertEqual(self.msg, expected) # Keep original assertion

if __name__ == "__main__":
    unittest.main()