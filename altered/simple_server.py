import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from ollama import Client
import time
from typing import List, Dict, Callable
import numpy as np
from functools import partial
from colorama import Fore, Style

ollama_client = Client(host='http://localhost:11434')

class Aggregations:
    @staticmethod
    def aggregate_embeddings(embeddings: List[List[float]], method: str, *args, **kwargs) -> List[float]:
        if method == 'sum':
            return np.sum(embeddings, axis=0).tolist()
        elif method == 'mean':
            return np.mean(embeddings, axis=0).tolist()
        # Return original list if method is unsupported
        return embeddings

    @staticmethod
    def create_aggregation_prompt(n: int, instruction: str, *args, **kwargs) -> str:
        instruct = (
            f"<INST>"
            f"You have been given a question or problem together with "
            f"a sample of {n} language model responses. "
            f"{instruction}"
            f"</INST>"
        )
        return instruct

    text_aggregations: Dict[str, Callable[[int], str]] = {
        'sum': partial(create_aggregation_prompt,
            instruction=(
                f"Aggregate all those responses into a single response. The response "
                f"should incorporate all relevant aspects from all provided "
                f"input responses no matter their relevance."
            )
        ),
        'mean': partial(create_aggregation_prompt,
            instruction=(
                f"Aggregate these responses into a single response. The response "
                f"should incorporate the more relevant aspects depending on their "
                f"mentioning frequency and elaboration within the input responses. "
                f"Leave out aspects that find no or little mention."
            )
        ),
        'max': partial(create_aggregation_prompt,
            instruction=(
                f"Find the text among the inputs that best addresses the question "
                f"or problem (best answer), and expand upon it, incorporating any "
                f"unique relevant information from the other responses."
            )
        ),
        'min': partial(create_aggregation_prompt,
            instruction=(
                f"Provide a concise summary that captures the core idea common to "
                f"all input responses, focusing on the most "
                f"essential information."
            )
        )
    }

    @classmethod
    def aggregate_text(cls, texts: List[str], method: str, model: str, *args, **kwargs) -> str | List[str]:
        if method in cls.text_aggregations:
            aggregation_prompt = cls.text_aggregations[method](len(texts))
            combined_texts = "\n\n".join(f"Response {i+1}: {text}" 
                                                            for i, text in enumerate(texts))
            final_prompt = (
                                f"{aggregation_prompt}\n\n"
                                f"Here are the input texts:\n\n"
                                f"{combined_texts}"
                            )
            
            # Use the Ollama client to generate the aggregated response
            response = ollama_client.generate(model=model, prompt=final_prompt)
            return response['response']
        
        return texts  # Return original list if method is unsupported

def validate_aggregation_method(method: str | None, domain: str, *args, **kwargs) -> bool:
    if method is None:
        return True
    if domain == 'get_embeddings':
        return method in ['sum', 'mean']
    elif domain == 'generates':
        return method in ['sum', 'mean', 'max', 'min']
    return False

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self, *args, **kwargs):
        overall_start = time.time()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        data = json.loads(post_data)
        sub_domain = self.path.split('/')[-1]
        prompts = data.get('prompt')
        model = data.get('model')
        aggregation_method = data.get('aggregation_method')
        
        if prompts is None or model is None:
            self.send_error(400, 'No prompt or model provided')
            return
        if not isinstance(prompts, list):
            self.send_error(400, 'Prompt should be a list of strings')
            return
        
        if not validate_aggregation_method(aggregation_method, sub_domain):
            print(  f"Warning: Unsupported aggregation method '{aggregation_method}' "
                    f"for {sub_domain}. Proceeding without aggregation.")
            aggregation_method = None
        
        responses = []
        try:
            for prompt in prompts:
                try:
                    if sub_domain == 'get_embeddings':
                        response = ollama_client.embeddings(model=model, prompt=prompt)
                        responses.append({'embedding': response['embedding']})
                    elif sub_domain == 'generates':
                        response = ollama_client.generate(model=model, prompt=prompt)
                        responses.append({'response': response['response']})
                except Exception as e:
                    print(f"An error occurred while processing prompt: {prompt}. Error: {e}")
                    responses.append({'error': str(e)})
            
            if aggregation_method:
                if sub_domain == 'get_embeddings':
                    aggregated_response = Aggregations.aggregate_embeddings(
                        [r['embedding'] for r in responses if 'embedding' in r], 
                        aggregation_method
                    )
                    responses.append(
                                        {   'embedding': aggregated_response,
                                            'aggregation_method': aggregation_method,
                                        }
                    )
                elif sub_domain == 'generates':
                    aggregated_response = Aggregations.aggregate_text(
                        [r['response'] for r in responses if 'response' in r], 
                        aggregation_method,
                        model=model
                    )
                    responses.append(
                                        {  'response': aggregated_response,
                                            'aggregation_method': aggregation_method,
                                        }
                    )
            
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
            self.send_error(500, str(e))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=5555, 
        *args, **kwargs
    ):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting the HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
