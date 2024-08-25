# test_altered.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
from altered.helpers.collections import group_text, handle_tags, pretty_print_messages
import altered.settings as sts
import altered.helpers.collections as hlp
import altered.test.testhelper as helpers
import logging


class Test_Unittest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.testData = cls.mk_test_data(*args, **kwargs)
        cls.assist_text = """
            Certainly! To create your package named `myclock` in your user directory, run the following command in your terminal:  ```shell pipenv run alter clone -pr 'myclock' -n 'myclock' -a 'myclk' -t 'C:\\Users\\lars' -p 3.11 --install ```  \nThis will clone `altered_bytes` to `C:/Users/lars/myclock`, set up the environment, and install dependencies.
        """

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.test_data_dir, "test_altered.yml"), "r") as f:
            out = yaml.safe_load(f)
        return out

    def test_pretty_print_messages(self, *args, **kwargs):
        messages = (
                    {'role': 'user', 'content': 'This is the user message.'},
                    {'role': 'assistant', 'content': self.assist_text},
                    )
        print(f"\n{sts.YELLOW}Pretty print messages:{sts.RESET}")
        # pretty_print_messages(messages, *args, verbose=1, **kwargs)

    def test_handle_tags(self):
        text = (
                f"<instructions> \nThese are your instructions\n </instructions>"
                f"There is also some fill text. <hierarchy> Some hierarchy.</hierarchy>"
                f"<pg_info> This is your pg_info </pg_info>"
                f"This is the actual question."
        )
        out = handle_tags(text)
        print(f"\n{sts.YELLOW}Doing nothing{sts.RESET}: {out}")
        out = handle_tags(text, tags=['pg_info'])
        print(f"\n{sts.YELLOW}Only pg_info{sts.RESET}: {out}")
        out = handle_tags(text, tags=['instructions', 'pg_info'])
        print(f"\n{sts.YELLOW}Instructions and pg_info{sts.RESET}: {out}")
        out = handle_tags(text, tags=['instructions', 'pg_info'], verbose=2)
        print(f"\n{sts.YELLOW}Instructions and pg_info verbose{sts.RESET}: {out}")

    def test_group_text(self):
        # NOTE: keep the first line at its current length for testing.

        out = group_text(self.assist_text, 70)
        print(f"\nGrouped self.assist_text: {out}")


if __name__ == "__main__":
    unittest.main()
