import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from ollama import Client
import time
from typing import List, Dict
from colorama import Fore, Style

# Configure the Ollama client to connect to the local server
ollama_client = Client(host='http://localhost:11434')  # Assuming Ollama is running on localhost on port 11434

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        overall_start = time.time()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        data = json.loads(post_data)

        # Extract sub-domain (either 'get_embeddings' or 'generate')
        sub_domain = self.path.split('/')[-1]

        prompts = data.get('prompt')
        model = data.get('model')

        # Validate inputs
        if prompts is None or model is None:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_msg = 'No prompt provided' if prompts is None else 'No model provided'
            self.wfile.write(json.dumps({'error': error_msg}).encode('utf-8'))
            return

        if not isinstance(prompts, list):
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Prompt should be a list of strings'}).encode('utf-8'))
            return

        responses = []
        try:
            for prompt in prompts:
                try:
                    if sub_domain == 'get_embeddings':
                        # Generate embeddings
                        response = ollama_client.embeddings(model=model, prompt=prompt)
                        responses.append(response)
                    elif sub_domain == 'generates':
                        # Generate text
                        response = ollama_client.generate(model=model, prompt=prompt)
                        responses.append(response)
                except Exception as e:
                    print(f"An error occurred while processing prompt: {prompt}. Error: {e}")
                    responses.append(None)

            overall_end = time.time()
            server_time = f"{overall_end - overall_start:.3f}"

            response_payload = json.dumps({
                'results': responses,
                'server_time': server_time
            })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response_payload.encode('utf-8'))
            print(f"send response: {server_time = }")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=5555):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting the HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
