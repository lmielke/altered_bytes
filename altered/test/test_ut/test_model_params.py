# test_model_settings.py

import os
import unittest
import yaml
from datetime import datetime as dt
import altered.model_params as msts
import altered.settings as sts
        
test_data_path = os.path.join(sts.test_data_dir, "test_model_settings.yml")
sts.models_config_path = test_data_path

class Test_ModelParams(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verbose = 0
        cls.test_data_path = test_data_path
        cls.api_key_path = os.path.join(sts.test_data_dir, "api_key.yml")
        cls.create_test_data()
        cls.test_inst = msts.ModelParams()
        # print(f"\n{sts.YELLOW}Test_ModelParams:{sts.RESET}: {msts.params.config}")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.api_key_path):
            os.remove(cls.api_key_path)

    @classmethod
    def create_test_data(cls):
        # Write test API key file
        with open(cls.api_key_path, "w") as f:
            yaml.safe_dump({'key': 'test_key_value'}, f)

        data = {
            'models': {
                'test_dolphin-llama3:8b-256k': {
                    'blob_id': '123456789',
                    'context_length': '9999',
                    'embedding_length': '4444',
                    'general.architecture': 'llama',
                    'general.file_type': 'Q99',
                    'last_update': '3 months ago',
                    'name': 'test_dolphin-llama3:8b-256k',
                    'new_update_available': False,
                },
            },
            'servers': {
                'test_server': {
                    'embedding_port': 1234,
                    'generate_port': 5678,
                    'model_address': 'http://localhost',
                    'models_to_load': ['test_dolphin-llama3:8b-256k'],
                    'key_path': None,
                },
                'openAI': {
                    'embedding_port': None,
                    'generate_port': None,
                    'model_address': None,
                    'models_to_load': None,
                    'key_path': cls.api_key_path,  # Use API key file path here
                }
            },
            'aliasses': {
                            'servers': {
                                'tst': 'test_server',
                                'oai': 'openAI'
                            },
                            'models': {
                                'tm': 'test_dolphin-llama3:8b-256k',
                            },
            },
            'defaults': {
              # default ollama server that comes with ollama,
                  'generate': {
                        'model': 'llama3.1:70b',
                        'server': 'while-ai_0',
                    },
                  # altered_bytes default server for generate responses,
                  'get_generates': {
                        'model': 'llama3.1:70b',
                        'server': 'while-ai_0',
                    },
                  # altered_bytes default server for embeddings,
                  'get_embeddings': {
                        'model': 'test_dolphin-llama3:8b-256k',
                        'server': 'test_server',
                    },
                  'service_endpoint': 'get_embeddings',
                  'keep_alive': 200,
            },
        }
        with open(cls.test_data_path, "w") as f:
            yaml.safe_dump(data, f)

    def test_load_model_configs(self):
        config = self.test_inst._load_model_configs(self.test_data_path)
        self.assertIsInstance(config, dict)
        self.assertIn('servers', config)
        self.assertIn('aliasses', config)
        self.assertEqual(config['servers']['test_server']['embedding_port'], 1234)
        self.assertEqual(config['aliasses']['servers']['tst'], 'test_server')

    def test_unpack_alias(self):
        model_name, server_name = self.test_inst.unpack_alias(alias='tm_tst')
        self.assertEqual(model_name, 'test_dolphin-llama3:8b-256k')
        self.assertEqual(server_name, 'test_server')

        model_name, server_name = self.test_inst.unpack_alias(alias='tm_oai')
        self.assertEqual(model_name, 'test_dolphin-llama3:8b-256k')
        self.assertEqual(server_name, 'openAI')

        with self.assertRaises(ValueError):
            self.test_inst.unpack_alias(alias='invalid_alias')

    def test_get_api_key(self):
        self.test_inst.config['servers']['openAI']['key_path'] = self.api_key_path
        # Ensure the get_api_key method works as expected
        result = self.test_inst.get_api_key()
        self.assertEqual(result, 'test_key_value')

    def test_update_servers(self):
        # Define the update parameters
        update_params = {
            'embedding_port': 2345,
            'generate_port': 6789,
            'model_address': 'http://newaddress',
            'key_path': 'new_key_path'
        }
        
        # Update server parameters
        self.test_inst.update_servers('test_server', update_params)

        # Validate the updates
        updated_params = self.test_inst.servers['test_server']
        self.assertEqual(updated_params['embedding_port'], 2345)
        self.assertEqual(updated_params['generate_port'], 6789)
        self.assertEqual(updated_params['model_address'], 'http://newaddress')
        self.assertEqual(updated_params['key_path'], 'new_key_path')
        self.assertEqual(self.test_inst.last_update, dt.now().strftime('%Y-%m-%d'))

        with self.assertRaises(ValueError):
            self.test_inst.update_servers('non_existent_server', update_params)

    # def test_get_model(self):
    #     # Test for 'test_server'
    #     self.maxDiff = None
    #     self.test_inst.config['servers']['test_server']['key_path'] = self.api_key_path
    #     result = self.test_inst.get_model('tm_tst')
    #     expected_params = {
    #             'model_file': {                   
    #                     'name': 'test_dolphin-llama3:8b-256k',
    #                     'blob_id': '123456789',
    #                     'last_update': '3 months ago',
    #                     'general.architecture': 'llama',
    #                     'general.file_type': 'Q99',
    #                     'context_length': '9999',
    #                     'embedding_length': '4444',
    #                     'new_update_available': False
    #                     },
    #             'server': 'test_server',
    #             'params': {
    #                 'embedding_port': 1234,
    #                 'generate_port': 5678,
    #                 'model_address': 'http://localhost',
    #                 'models_to_load': ['test_dolphin-llama3:8b-256k'],
    #                 'key_path': self.api_key_path,
    #             },
    #     }
    #     self.assertEqual(result, expected_params)

    #     # Test for 'openAI'
    #     result = self.test_inst.get_model('tm_oai')
    #     expected_params = {
    #             'model_file': {                   
    #                     'name': 'test_dolphin-llama3:8b-256k',
    #                     'blob_id': '123456789',
    #                     'last_update': '3 months ago',
    #                     'general.architecture': 'llama',
    #                     'general.file_type': 'Q99',
    #                     'context_length': '9999',
    #                     'embedding_length': '4444',
    #                     'new_update_available': False
    #                     },
    #             'server': 'openAI',
    #             'params': {
    #                 'api_key': 'test_key_value',
    #             },
    #     }
    #     self.assertEqual(result, expected_params)

    #     with self.assertRaises(ValueError):
    #         self.test_inst.get_model('invalid_alias')

    # def test_extract_model_info(self):
    #     url = "https://ollama.com/library/llama3.1/blobs/8eeb52dfb3bb"
    #     info = self.test_inst.extract_model_info('tm_tst', url)

    def test_string_to_days(self):
        age_string = '5 days ago'
        result = self.test_inst.string_to_days(age_string)
        self.assertEqual(result, 5)

        age_string = '8 weeks ago'
        result = self.test_inst.string_to_days(age_string)
        self.assertEqual(result, 56)

        age_string = '3 months ago'
        result = self.test_inst.string_to_days(age_string)
        self.assertEqual(result, 90)


if __name__ == "__main__":
    unittest.main()

# print(msts.config.get_model('l38b_0'))
# print(msts.config.api_key)