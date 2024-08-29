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
    def aggregate_embeddings(embeddings:List[List[float]], method:str, *args, **kwargs,
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

    @staticmethod
    def create_aggregation_prompt(n:int, instruction:str, *args, **kwargs) -> str:
        instruct = (
            f"<INST>"
            f"You have been given a question or problem together with "
            f"a sample of {n} language model responses. Your task is to:"
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
        ),
        'std': partial(create_aggregation_prompt,
            instruction=(
                f"Estimate the semantic deviation between the provided responses (std).\n"
                f"STD here is an integer value (from 0 to 3) for the semantic deviation.\n"
                f"\t- 0: No deviation, responses are extremely similar or even identical.\n"
                f"\t- 1: Low deviation, responses are similar but differ in some details. "
                f" For example, one answer might go deeper or explain additional aspects.\n"
                f"\t- 2: Moderate deviation, responses differ in several aspects. "
                f"Some outliers might even differ in their overall topic.\n"
                f"\t- 3: High deviation, responses are very different, mostly describing "
                f"different unrelated topics.\n"
                f"Respond with a json string containing the std value and your reasoning! \n"
                f"Example: {{'responses_std': '1', 'reasoning': 'The responses ...'}}"
            )
        )
    }

    @classmethod
    def aggregate_text(cls, prompts:List[str], responses:List[str], 
                            method:str, model:str, *args, 
                            **kwargs
        ) -> str | List[str]:
        """
        This function aggregates multiple text responses into a single one.
        Sometimes sampling multiple responses from a language model can provide
        a more comprehensive answer to a question or problem. This function
        aggregates those responses into a single one.
        """
        if method in cls.text_aggregations:
            aggregation_prompt = cls.text_aggregations[method](len(prompts))
            combined_texts = "\n\n".join(
                f"Prompt {i+1}: {pr}\nResponse {i+1}: {rs}"
                for i, (pr, rs) in enumerate(zip(prompts, responses))
            )
            final_prompt = (
                f"{aggregation_prompt}\n\n"
                f"Here are the input texts:\n\n"
                f"{combined_texts}"
            )
            # Use the Ollama client to generate the aggregated response
            response = ollama_client.generate(model=model, prompt=final_prompt)
            return response['response']
        # Return original list if method is unsupported
        return responses


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self, *args, **kwargs):
        overall_start = time.time()
        try:
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            sub_domain = self.path.split('/')[-1]
            prompts = data.get('prompt')
            model = data.get('model')
            aggregation_method = data.get('aggregation_method')
            # General input validations
            if prompts is None or model is None:
                self.send_error(400, 'No prompt or model provided')
                return
            if not isinstance(prompts, list):
                self.send_error(400, 'Prompt should be a list of strings')
                return
            # Generate responses
            responses = self.respond(prompts, sub_domain, model)
            # Process the original aggregation method
            self.process_responses(prompts, responses, sub_domain, aggregation_method, model)
            # Process the std aggregation
            if len(responses) >= 2 and aggregation_method != 'std':
                # if an aggregation record exists, it needs to be excluded from std calc
                self.process_responses(prompts, responses, sub_domain, 'std', model)
            # Generate the response payload
            response_payload = self.mk_payload(responses, overall_start)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response_payload.encode('utf-8'))
        
        except Exception as e:
            print(f"An error occurred: {e}")
            self.send_error(500, str(e))

    def mk_payload(self, responses:List[Dict[str, str]], overall_start:float) -> str:
        overall_end = time.time()
        server_time = f"{overall_end - overall_start:.3f}"
        response_payload = json.dumps({
            'results': responses,
            'server_time': server_time
        })
        return response_payload
    
    def respond(self, prompts:List[str], sub_domain:str, model:str) -> List[Dict[str, str]]:
        responses = []
        try:
            for prompt in prompts:
                try:
                    if sub_domain == 'get_embeddings':
                        response = ollama_client.embeddings(model=model, prompt=prompt)
                        responses.append({'prompt': prompt, 'embedding': response['embedding']})
                    elif sub_domain == 'generates':
                        response = ollama_client.generate(
                                                            model=model, 
                                                            prompt=prompt,
                                                            options=options,
                                                            stream=stream,
                                    )
                        responses.append({'prompt': prompt, 'response': response['response']})
                except Exception as e:
                    print(f"An error occurred while processing prompt: {prompt}. Error: {e}")
                    responses.append({'prompt': prompt, 'error': str(e)})
        except Exception as e:
            print(f"An error occurred during response generation: {e}")
        return responses

    def process_responses(self, prompts:List[str], responses:List[str], sub_domain:str, 
                                aggregation_method:str, model:str,
                                *args, **kwargs,
        ) -> None:
        """
        This function processes multiple responses generated by the language model.
        It performes aggregations as well as statistical analysis on the responses.
        NOTE: std (Standard Deviation) is technically handled like an aggregation_method 
        even so it is not a real aggregation.
        """
        if not aggregation_method:
            return
        # Only the original prompts responses should be considered not appended aggregation records
        slc = slice(None, len(prompts))
        # Extract the embeddings from the responses dictionary
        if sub_domain == 'get_embeddings':
            aggregated_response = Aggregations.aggregate_embeddings(
                [r['embedding'] for r in responses[slc] if 'embedding' in r], 
                aggregation_method
            )
            responses.append(
                {   
                    'embedding': aggregated_response,
                    'aggregation_method': aggregation_method,
                }
            )
        elif sub_domain == 'generates':
            # Extract the responses from the responses dictionary
            aggregated_response = Aggregations.aggregate_text(
                prompts, 
                [r['response'] for r in responses[slc] if 'response' in r], 
                aggregation_method,
                model=model
            )
            responses.append(
                {  
                    'response': aggregated_response,
                    'aggregation_method': aggregation_method,
                }
            )

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=5555, 
        *args, **kwargs
    ):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting the HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
