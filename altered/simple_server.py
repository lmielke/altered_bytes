import json, os, time, yaml
from http.server import BaseHTTPRequestHandler, HTTPServer
from ollama import Client
from typing import List, Dict
import numpy as np
from colorama import Fore, Style

olc = Client(host='http://localhost:11434')


class Aggregations:


    def __init__(self, *args, **kwargs):
        agg_file_name = 'prompt_aggreg.yaml'
        self.prompt_aggreg = self.load_prompt_aggreg(agg_file_name, *args, **kwargs)

    def load_prompt_aggreg(self, agg_file_name, *args, **kwargs):
        prompt_aggreg_dir = os.path.join(
                                                os.path.dirname(__file__), 
                                                'resources',
                                                'strategies',
                                                )
        with open(os.path.join(prompt_aggreg_dir, agg_file_name), 'r') as file:
            return yaml.safe_load(file)

    def aggregate_embeddings(self, embeddings: List[List[float]], method: str, *args, **kwargs
        ) -> List[float]:
        """
        In some cases we might want to have a more balanced representation of the 
        embeddings. This function provides a way to aggregate multiple embeddings 
        into a single one.

        Check if these statistical methods make even sense.
        """
        if method == 'sum':
            return np.sum(embeddings, axis=0).tolist()
        elif method == 'mean':
            return np.mean(embeddings, axis=0).tolist()
        elif method == 'std':
            return np.std(embeddings, axis=0).tolist()
        # Return original list if method is unsupported
        return embeddings

    def create_aggregation_prompt(self, n: int, agg_method: str) -> str:
        instruction = self.prompt_aggreg.get(agg_method, "")
        if not instruction:
            return None
        else:
            instruct = (
                        f"<INST>"
                            f"You have been given a question or problem together with "
                            f"a sample of {n} language model responses. Your task is to:"
                                f"{instruction['prompt']}\n"
                            f"Follow the instructions closely! "
                            f"Do not use any introduction/greeting phrases."
                        f"</INST>"
        )
        return instruct

    def aggregate_text(self, prompts: List[str], responses: List[str], agg_method: str, 
                       options: dict, *args, **kwargs) -> str | List[str]:
        """
        This function aggregates multiple text responses into a single one.
        Sometimes sampling multiple responses from a language model can provide
        a more comprehensive answer to a question or problem. This function
        aggregates those responses into a single one.
        """
        if agg_method in self.prompt_aggreg:
            aggregation_prompt = self.create_aggregation_prompt(len(prompts), agg_method)
            combined_texts = "\n\n".join(
                f"Prompt {i+1}: {prompt}\nResponse {i+1}: {response}"
                for i, (prompt, response) in enumerate(zip(prompts, responses))
            )
            final_prompt = (
                f"{aggregation_prompt}\n\n"
                f"Here are the input texts:\n\n"
                f"{combined_texts}"
            )
            num_predict_mult = self.prompt_aggreg[agg_method].get('num_predict_mult', 2)
            # Use the Ollama client to generate the aggregated response
            if agg_method in ['max', 'mean']:
                options['num_predict'] = options.get('num_predict', 100) * num_predict_mult
            response = olc.generate(prompt=final_prompt, options=options, **kwargs)
            return response['response']
        # Return original list if agg_method is unsupported
        return responses

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    aggregations = None  # This will be set when the server starts

    def do_POST(self, *args, **kwargs):
        network_up_time, start_time = self.set_times(*args, **kwargs)
        try:
            kwargs.update(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
            # General input validations
            if not self.successful_server_validations(*args, **kwargs):
                return
            # Generate responses
            responses = self.respond(*args, **kwargs)
            # Process the original aggregation method
            self.process_responses(*args, responses=responses, **kwargs)
            # Process the std aggregation
            self.get_response_stats(*args, responses=responses, **kwargs)
            # Generate the response payload
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(self.mk_payload(
                                                responses, 
                                                network_up_time, 
                                                start_time
                                )
            )
        
        except Exception as e:
            print(f"An error occurred: {e}")
            self.send_error(500, str(e))

    def set_times(self, *args, network_up_time, **kwargs):
        start_time = time.time()
        network_up_time = network_up_time - start_time
        return network_up_time, start_time


    def successful_server_validations(self, *args, model: str, prompts: List[str], **kwargs
        ) -> bool:
        if prompts is None or model is None:
            self.send_error(400, 'No prompt or model provided')
            return False
        if not isinstance(prompts, list):
            self.send_error(400, 'Prompt should be a list of strings')
            return False
        return True

    def get_response_stats(self, *args, responses:List[Dict[str, str]], agg_method:str=None, 
                                **kwargs
        ):
        # if an aggregation record exists, it needs to be excluded from std calc
        if len(responses) >= 2 and agg_method != 'std':
            kwargs['agg_method'] = 'std'
            self.process_responses(*args, responses=responses, **kwargs)

    def mk_payload(self, responses: List[Dict[str, str]],
                            network_up_time: float,
                            start_time: float
        ) -> bytes:
        response_payload = json.dumps({
            'results': responses,
            'network_up_time': network_up_time,
            'network_down_time': time.time(),
            'total_server_time': f"{time.time() - start_time:.3f}"
        })
        return response_payload.encode('utf-8')
    
    def respond(self, *args, prompts:List[str], sub_domain:str, options:dict, 
                agg_method:str=None, **kwargs,
        ) -> List[Dict[str, str]]:
        responses = []
        try:
            for prompt in prompts:
                options['seed'] = np.random.randint(0, 1000)
                try:
                    if sub_domain == 'get_embeddings':
                        response = olc.embeddings(prompt=prompt, options=options, **kwargs)
                        responses.append(
                            {
                                'prompt': prompt, 
                                'embedding': response['embedding'],
                                'temperature': options['temperature']
                            }
                        )
                    elif sub_domain == 'generates':
                        response = olc.generate(prompt=prompt, options=options, **kwargs)
                        responses.append(
                            {
                                'prompt': prompt, 
                                'response': response['response'],
                                'temperature': options['temperature']
                            }
                        )
                except Exception as e:
                    print(f"An error occurred while processing prompt: {prompt}. Error: {e}")
                    responses.append({'prompt': prompt, 'error': str(e)})
        except Exception as e:
            print(f"An error occurred during response generation: {e}")
        return responses

    def process_responses(self, *args, prompts:List[str], responses:List[str], sub_domain:str, 
                          model:str, agg_method:str=None, **kwargs) -> None:
        """
        This function processes multiple responses generated by the language model.
        It performs aggregations as well as statistical analysis on the responses.
        NOTE: std (Standard Deviation) is technically handled like an agg_method 
        even so it is not a real aggregation.
        """
        if not agg_method:
            return
        # Only the original prompts and responses are considered, NOT aggregation records
        slc = slice(None, len(prompts))
        # get_embeddings returns a vector, so here we perform a statistical aggregation
        if sub_domain == 'get_embeddings':
            agg_response = self.aggregations.aggregate_embeddings(
                [r['embedding'] for r in responses[slc] if 'embedding' in r], 
                agg_method,
            )
            # agg_method is added to mark the record as an aggregation record
            responses.append({'embedding': agg_response, 'agg_method': agg_method})
        # generate gets texts, so here we perform a semantic aggregation
        elif sub_domain == 'generates':
            # Extract the responses from the responses dictionary
            agg_response = self.aggregations.aggregate_text(
                prompts, 
                [r['response'] for r in responses[slc] if 'response' in r], 
                agg_method,
                model=model,
                **kwargs,
            )
            # agg_method is added to mark the record as an aggregation record
            responses.append({'response': agg_response, 'agg_method': agg_method})

class AggregationsHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RequestHandlerClass.aggregations = Aggregations(*args, **kwargs)

def run(server_class=AggregationsHTTPServer, handler_class=SimpleHTTPRequestHandler, port=5555, 
        *args, **kwargs):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting the HTTP server on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()