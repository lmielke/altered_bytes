# api_quick.py
from altered.model_connect import SingleModelConnect

def main(*args, user_prompt:str, **kwargs) -> str:
    if user_prompt is None:
        raise AttributeError("Ask a question! -up 'What is the meaning of life?'")
    assi = SingleModelConnect(*args, **kwargs)
    server_params = {'service_endpoint': 'get_generates', 
                        'repeats': {'num': 1, 'agg': None}, 
                        'temperature': 0.1, 'bias':0.0, 'scale':1, 'verbose': 0, 
                        'num_predict': 250, 'alias': 'l3.2_0', 'fmt': 'markdown'}
    r = assi.post(user_prompt, *args, **server_params)
    if r.get('responses'):
        response = r.get('responses')[0]['response']
    return response
