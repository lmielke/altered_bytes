from altered.model_connect import SingleModelConnect

def main(*args, user_prompt: str, **kwargs) -> str:
    if not user_prompt:
        raise AttributeError("Ask a question! Use: -up 'What is the meaning of life?'")

    assi = SingleModelConnect(*args, **kwargs)
    server_params = {
        'service_endpoint': 'get_generates',
        'repeats': {'num': 1, 'agg': None},
        'temperature': 0.1,
        'bias': 0.0,
        'scale': 1,
        'verbose': 0,
        'num_predict': 250,
        'alias': 'l3.2_1',
        'fmt': 'markdown',
        'messages': [user_prompt]  # explicitly pass as 'messages'
    }

    r = assi.post(*args, **server_params)
    print(f"{r = }")
    if r.get('responses'):
        return r['responses'][0].get('response', '')
    return ''
