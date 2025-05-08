# test_info_git_diff.py

import os, re, shutil, sys, time, yaml
import unittest

# test package imports
import altered.settings as sts
import altered.hlp_printing as hlpp

from altered.info_git_diff import GitDiffs
from altered.prompt_tool_choice import FunctionToJson


class Test_GitDiffs(unittest.TestCase):
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
        # with open(os.path.join(sts.test_data_dir, "test_info_git_diff.yml"), "r") as f:
        #     out = yaml.safe_load(f)
        return out

    def test___init__(self, *args, **kwargs):
        expected = False
        out = True
        self.assertEqual(self.msg, expected)

    def test_extract_git_status(self, *args, **kwargs):
        """
        Test the extraction of git status output.

        Args:
            self (Test_GitDiffs): Test class instance.
        """
        gd = GitDiffs()
        out = gd.extract_git_status()
        assert isinstance(out, str)
        assert "Error" not in out

    def test_parse_git_status(self, *args, **kwargs):
        expected = False
        out = True
        self.assertEqual(self.msg, expected)

    def test_get_git_status(self, *args, **kwargs):
        expected = False
        out = True
        self.assertEqual(self.msg, expected)

    def test_extract_git_diff(self, *args, **kwargs):
        expected = False
        out = True
        self.assertEqual(self.msg, expected)

    def test_parse_git_diff(self, *args, **kwargs):
        expected = False
        out = True
        self.assertEqual(self.msg, expected)

    def test_escape_jinja_syntax(self, *args, **kwargs):
        expected = False
        out = True
        self.assertEqual(self.msg, expected)

    @FunctionToJson(schemas={"openai"}, write=True)
    def test_get_git_diffs(self, *args, **kwargs):
        expected = False
        out = True
        self.assertEqual(self.msg, expected)


if __name__ == "__main__":
    unittest.main()
