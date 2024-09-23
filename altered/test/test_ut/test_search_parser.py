import os, unittest, yaml
from unittest.mock import patch

# Assuming sts is correctly defined in the altered.settings
import altered.settings as sts
import altered.hlp_printing as hlpp
from altered.search_parser import Parser

class Test_Parser(unittest.TestCase):
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
        # Load the test URLs from the YAML file
        test_file_path = os.path.join(sts.test_data_dir, "test_search_parser.yml")
        with open(test_file_path, "r") as f:
            return yaml.safe_load(f)

    def test___init__(self, *args, **kwargs):
        """
        Test if the Parser class initializes properly.
        """
        parser = Parser()
        self.assertIsInstance(parser, Parser)

    def test_parse_site(self, *args, **kwargs):
        """
        Test the parse_site method to ensure it fetches and parses the content correctly.
        """
        parser = Parser()
        test_url = self.test_data['urls'][0]  # Use one of the URLs from the test data
        parsed_content = parser.parse_site(test_url)

        # Check if the parsed content is not empty and contains text
        self.assertTrue(len(parsed_content) > 0)
        self.assertIn(" ", parsed_content)  # Ensure there's some readable content

    def test_parse_urls(self, *args, **kwargs):
        """
        Test the parse_urls method to ensure it processes multiple URLs in parallel.
        """
        parser = Parser()
        url_dict = {url: None for url in self.test_data['urls']}  # Create a dict with URLs and None values

        # Call the method and get the parsed content
        parsed_url_dict = parser.parse_urls(url_dict, max_workers=3)

        # Check if all URLs have been parsed (i.e., the None values have been replaced)
        for url, content in parsed_url_dict.items():
            self.assertIsNotNone(content)  # The content should not be None
            self.assertTrue(len(content) > 0)  # The content should not be empty
            self.assertIn(" ", content)  # Ensure there's some readable content
            hlpp.dict_to_table('test_parse_urls', parsed_url_dict, max_chars=200)


if __name__ == "__main__":
    unittest.main()
