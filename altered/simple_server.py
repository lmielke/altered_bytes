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
        'max': partial(create_aggregation_prompt,
            instruction=(
                f"Provide a comprehensive summary that captures the summary of all ideas "
                f"provided by all input responses, include all aspects regardless "
                f"of their relevance. "
                f"Only leave out aspects that are obviously completely irrelevant."
            )
        ),
        'min': partial(create_aggregation_prompt,
            instruction=(
                f"Provide a concise summary that captures the core idea common to "
                f"all or most input responses! Focus on the most essential information."
            ),
        ),
        'mean': partial(create_aggregation_prompt,
            instruction=(
                f"Aggregate these responses into a single response. The response "
                f"should incorporate the more relevant aspects depending on their "
                f"mentioning frequency and elaboration within the input responses. "
                f"Leave out aspects that find no or little mention."
            )
        ),
        'best': partial(create_aggregation_prompt,
            instruction=(
                f"Find the text among the inputs that best addresses the question "
                f"or problem (best answer), and expand upon it, incorporating any "
                f"unique relevant information from the other responses."
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
    def aggregate_text(cls, prompts:List[str], responses:List[str], agg_method:str, 
                            options:dict, *args, **kwargs
        ) -> str | List[str]:
        """
        This function aggregates multiple text responses into a single one.
        Sometimes sampling multiple responses from a language model can provide
        a more comprehensive answer to a question or problem. This function
        aggregates those responses into a single one.
        """
        if agg_method in cls.text_aggregations:
            aggregation_prompt = cls.text_aggregations[agg_method](len(prompts))
            combined_texts = "\n\n".join(
                f"Prompt {i+1}: {prompt}\nResponse {i+1}: {response}"
                for i, (prompt, response) in enumerate(zip(prompts, responses))
            )
            final_prompt = (
                f"{aggregation_prompt}\n\n"
                f"Here are the input texts:\n\n"
                f"{combined_texts}"
            )
            # Use the Ollama client to generate the aggregated response
            if agg_method in ['max', 'mean']:
                options['num_predict'] = options.get('num_predict', 100) * 2
            response = ollama_client.generate(prompt=final_prompt, options=options, **kwargs)
            return response['response']
        # Return original list if agg_method is unsupported
        return responses


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self, *args, **kwargs):
        start_time = time.time()
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
            self.wfile.write(self.mk_payload(responses, start_time))
        
        except Exception as e:
            print(f"An error occurred: {e}")
            self.send_error(500, str(e))

    def successful_server_validations(self, *args, model:str, prompts:List[str], **kwargs) -> bool:
        if prompts is None or model is None:
            self.send_error(400, 'No prompt or model provided')
            return False
        if not isinstance(prompts, list):
            self.send_error(400, 'Prompt should be a list of strings')
            return False
        return True

    def get_response_stats(self, *args, responses:List[Dict[str, str]], agg_method:str, **kwargs):
        # if an aggregation record exists, it needs to be excluded from std calc
        if len(responses) >= 2 and agg_method != 'std':
            kwargs['agg_method'] = 'std'
            self.process_responses(*args, responses=responses, **kwargs)

    def mk_payload(self, responses:List[Dict[str, str]], start_time:float) -> str:
        response_payload = json.dumps({
            'results': responses,
            'server_time': f"{time.time() - start_time:.3f}"
        })
        return response_payload.encode('utf-8')
    
    def respond(self, *args, prompts:List[str], sub_domain:str, agg_method:str, options:dict, **kwargs,
        ) -> List[Dict[str, str]]:
        responses = []
        try:
            for prompt in prompts:
                options['seed'] = np.random.randint(0, 1000)
                try:
                    if sub_domain == 'get_embeddings':
                        response = ollama_client.embeddings(prompt=prompt, options=options, **kwargs)
                        responses.append(
                                            {
                                                'prompt': prompt, 
                                                'embedding': response['embedding'],
                                                'temperature': options['temperature']
                                            }
                                        )
                    elif sub_domain == 'generates':
                        response = ollama_client.generate(prompt=prompt, options=options, **kwargs)
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
                                agg_method:str, model:str,
                                **kwargs,
        ) -> None:
        """
        This function processes multiple responses generated by the language model.
        It performes aggregations as well as statistical analysis on the responses.
        NOTE: std (Standard Deviation) is technically handled like an agg_method 
        even so it is not a real aggregation.
        """
        if not agg_method:
            return
        # Only the original prompts and responses are considered, NOT aggregation records
        slc = slice(None, len(prompts))
        # get_embeddings returns a vector,so here we perform a statistical aggregation
        if sub_domain == 'get_embeddings':
            agg_response = Aggregations.aggregate_embeddings(
                            [r['embedding'] for r in responses[slc] if 'embedding' in r], 
                            agg_method,
            )
            # agg_method is added to mark the record as an aggregation record
            responses.append({'embedding': agg_response, 'agg_method': agg_method, } )
        # generate gets texts, so here we perform a semantic aggreation
        elif sub_domain == 'generates':
            # Extract the responses from the responses dictionary
            agg_response = Aggregations.aggregate_text(
                                prompts, 
                                [r['response'] for r in responses[slc] if 'response' in r], 
                                agg_method,
                                model=model,
                                **kwargs,
            )
            # agg_method is added to mark the record as an aggregation record
            responses.append({'response': agg_response, 'agg_method': agg_method, } )

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=5555, 
        *args, **kwargs
    ):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting the HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
