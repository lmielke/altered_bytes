# test_pre_ollama_server.py

import unittest, http.client, json, threading, time
from colorama import Fore, Style
from altered.pre_ollama_server import run, ServiceHTTPServer, SimpleHTTPRequestHandler


class Test_Ollama_Server(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.server_port = 5555
        cls.server_thread = threading.Thread(
            target=run, 
            args=(ServiceHTTPServer, SimpleHTTPRequestHandler, cls.server_port),
            kwargs={}
        )
        cls.server_thread.daemon = True  # Use daemon attribute instead of setDaemon (deprecated)
        cls.server_thread.start()
        time.sleep(1)  # Allow the server to start up before sending requests

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        # No specific teardown needed here, as the daemon thread will close with the test process.
        pass

    def test_ping_endpoint(self):
        """
        Test the /ping endpoint and validate the 'pong' response.
        """
        url = f"http://192.168.0.245:{self.server_port}"
        url = f"localhost:{self.server_port}"
        print(url)
        connection = http.client.HTTPConnection(url)
        headers = {"Content-Type": "application/json"}
        endpoint = 'get_generates'
        endpoint = 'ping'
        endpoint = 'unittest'

        # Include network_up_time in the POST data
        network_up_time = time.time()
        payload = json.dumps({
                                'network_up_time': network_up_time,
                                'strat_templates': ['agg_mean'],
                                'repeats': 3,
                                'prompts': ['Why is the sky blue?',],
                                'responses': [
                                                'Because of Rayleigh scattering.',
                                                'Because its not red.',
                                                'I dont know.'
                                                ],
                                'keep_alive': 200,
                                'stream': False,
                                'model': 'llama3.1',
                                'fmt': 'json',
                                'options': {
                                                'temperature': .2,
                                                'num_ctx': 8000,
                                            } ,
                                }).encode('utf-8')

        connection.request("POST", f"/{endpoint}", body=payload, headers=headers)
        response = connection.getresponse()

        # Validate response status and content
        self.assertEqual(response.status, 200, "Expected status code 200")
        response_data = json.loads(response.read().decode())
        time.sleep(0.01)
        response_data['network_down_time'] = f"{time.time() - float(response_data['network_down_time']):.3f}"
        print(f"Response data: {response_data}")
        for i, r in enumerate(response_data['responses']):
            print(f"\n{Fore.YELLOW}{i}:{Fore.RESET} {r}")
        self.assertIn('responses', response_data, "Response must contain 'responses' key")
        self.assertEqual(response_data['responses'][0]['response'], 'pong', "Expected response to be 'pong'")
        self.assertIn('prompt_counter', response_data, "Response must contain 'prompt_counter' key")
        self.assertGreaterEqual(response_data['prompt_counter'][endpoint], 1, "Ping count should be >= 1")

        # Check that the network_up_time was calculated correctly
        self.assertIn('network_up_time', response_data, "Response must contain 'network_up_time' key")
        elapsed_time = float(response_data['network_up_time'])
        self.assertGreater(elapsed_time, 0, "Elapsed network time should be greater than 0")

if __name__ == '__main__':
    unittest.main()
