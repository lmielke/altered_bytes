"""
prompt_strategies.py
Creates the self.strat dictionary that is a sub-dict of self.context in Instructions class.
As such it is used to render the prompt instructions for the user.
"""
import os, re, yaml
import altered.settings as sts
from colorama import Fore, Style

from altered.yml_parser import YmlParser

class Strategy:

    fmts = {'json': '# ...', 'yaml': '# ...', 'yml': '# ...', 'markdown': '> ...'}
    s_types = {'outputs', 'instructs'}
    s_type, s_name = None, None
    jinja_var = r'(^\w+)(?::\s*\\)(\{\{ \w+ \}\})(\s*$)'

    def __init__(self, *args, **kwargs):
        self.strats = {}
        self.templates = {}

    def __call__(self, *args, **kwargs):
        self.mk_strat_params(*args, **kwargs)
        self.load_strat(*args, **kwargs)
        return self.mk_context(*args, **kwargs)

    def mk_strat_params(self, strat_template_name:str, *args, **kwargs):
        self.template_name = strat_template_name
        self.template_file_name = f'{strat_template_name}.yml'
        self.template_path = os.path.join(sts.strats_dir, self.template_file_name)
        self.s_type, self.key = strat_template_name.split('_', 1)

    def load_strat(self, *args, fmt='markdown', **kwargs):
        loader = YmlParser(*args, fields_paths=[self.template_path], **kwargs)
        self.strats['method'] = {
                                                'body': loader.describe(fmt=fmt),
                                                'meta': loader.fields.get('meta'),
                                                'data': loader.data,
                                            }
        self.strats['fmt_comment'] = f'''"{self.fmts.get(fmt, '# ...')}"'''

    def mk_context(self, *args, fmt:str=None, **kwargs):
        if fmt is not None:
            self.strats['fmt'] = fmt
        self.strats['key'] = self.key
        return self.strats

class Default(Strategy):
    pass

class Agg(Strategy):

    strat_tag = 'sample'
    """
    Generates the Aggregation instantiation of Strategy.strats dict to render a Aggregation
    instruction.
    Aggregation refers to condensing multiple prompts into a single prompt.
    """
    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        return self.mk_prompt_agg_instruct(*args, **kwargs)

    def mk_prompt_agg_instruct(self, *args, **kwargs) -> dict:
        """
        Generates aggregation prompt based on the specified strategy.
        """
        num_responses = len(kwargs['responses'])
        self.strats['strat_tag'] = self.strat_tag
        self.strats['inputs_intro'] = (
                            f"Below is the {self.strat_tag} of {num_responses} "
                            f"of an LLM`s responses "
                        )
        if not kwargs.get('prompts'):
            self.strats['inputs'] = self.mk_sample_no_prompt(*args, **kwargs)
            self.strats['inputs_intro'] += (
                        f"that need to be aggregated. "
                        f"Note, that there is no prompt associated with these responses. "
                        f"Therefore you have to infer the prompt from other information, "
                        f"i.e. the responses, name or search query."
                                            )
            self.strats['inputs_header'] = f"Texts to aggregate:"
        if len(kwargs['prompts']) == 1:
            self.strats['inputs'] = self.mk_sample_single_prompt(*args, **kwargs)
            self.strats['inputs_intro'] += f"intending to answer the same single prompt."
            self.strats['inputs_header'] = f"Answers to a single prompt:"
        elif len(kwargs['prompts']) > 1:
            self.strats['inputs'] = self.mk_sample_multi_prompt(*args, **kwargs)
            self.strats['inputs_intro'] += f"intending to answer {num_responses} prompts."
            self.strats['inputs_header'] = f"Answers and prompts:"
        else:
            self.strats['inputs'] = self.mk_sample_no_prompt(*args, **kwargs)
        return self.strats

    def mk_sample_multi_prompt(self, *args, prompts:list, responses:list, rm_tags:bool=False, **kwargs):
        """
        Takes in a list of prompts and responses and returns a string that
        represents a bullet point list of the provided prompts and responses. This structures
        the prompts and responses in a easy to understand way to allow the LLM to aggregate.
        Example output:
        ## Sample of Provided Answers:
        Prompt 1: Why is the sky blue?
        Response 1: The sky is blue because of Rayleigh scattering.

        Prompt 2: How many stars are in the sky?
        Response 2: There are an infinite number of stars in the sky.
        """
        # print(f"{Fore.RED}prompts multi:{Fore.RESET} {prompts}")
        sample_pairs = []
        for i, (prompt, resp) in enumerate(zip(prompts, responses)):
            if rm_tags:
                prompt = self.rm_tags(prompt, *args, **kwargs)
            sample_pairs.append(
                                    f"\n__SAMPLE {i+1}__\n\n"
                                    f"Prompt {i+1}: {prompt}\n"
                                    f"Response {i+1}: {resp}"
                                )
        return '\n\n'.join(sample_pairs)

    def mk_sample_single_prompt(self, *args, prompts:str, responses:list, rm_tags:bool=False, **kwargs):
        """
        Takes in a list of prompts and responses and returns a string that
        represents a bullet point list of the provided prompts and responses. This structures
        the prompts and responses in a easy to understand way to allow the LLM to aggregate.
        Example output:
        ## Sample of Provided Answers:
        Prompt 1: Why is the sky blue?
        Response 1: The sky is blue because of Rayleigh scattering.

        Prompt 2: How many stars are in the sky?
        Response 2: There are an infinite number of stars in the sky.
        """
        # print(f"{Fore.RED}prompt single:{Fore.RESET} {prompts}")
        
        samples = []
        if rm_tags:
            prompt = self.rm_tags(prompts[0], *args, **kwargs)
        else:
            prompt = prompts[0]
        for i, response in enumerate(responses):
            samples.append(
                            f"\n__RESPONSE SAMPLE {i+1}__\n"
                            f"{response}"
                            )
        return f"\nPrompt: {prompt}\n\n" + '\n'.join(samples)

    def mk_sample_no_prompt(self, *args, responses:list, **kwargs):
        """
        Takes in a list of prompts and responses and returns a string that
        represents a bullet point list of the provided prompts and responses. This structures
        the prompts and responses in a easy to understand way to allow the LLM to aggregate.
        Example output:
        ## Sample of Provided Answers:
        Prompt 1: Why is the sky blue?
        Response 1: The sky is blue because of Rayleigh scattering.

        Prompt 2: How many stars are in the sky?
        Response 2: There are an infinite number of stars in the sky.
        """
        # print(f"{Fore.RED}prompt none:{Fore.RESET} {responses}")
        
        samples = []
        for i, response in enumerate(responses):
            samples.append(
                            f"\n__TEXT SAMPLE {i+1}__\n"
                            f"{response}"
                            )
        return '\n'.join(samples)

    def rm_tags(self, prompt:str, *args, **kwargs):
        tags = ['context', 'user_prompt', 'sample', 'response_template', 'INST']
        for tag in tags:
            prompt = prompt.replace(f"<{tag}>", "").replace(f"</{tag}>", "")
        return prompt

class Reduce(Strategy):

    strat_tag = 'de_noise_text'
    """
    Generates the Aggregation instantiation of Strategy.strats dict to render a Aggregation
    instruction.
    Aggregation refers to condensing multiple prompts into a single prompt.
    """
    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        return self.mk_prompt_reduce_instruct(*args, **kwargs)

    def mk_prompt_reduce_instruct(self, *args, 
                                            responses:list,
                                            user_prompt:str=None,
                                            link:str=None,
                                            rm_tags:bool=False,
                                            search_query:str=None, **kwargs,
        ) -> dict:
        """
        Generates aggregation prompt based on the specified strategy.
        """
        resp = responses[0]
        headers = ''
        if user_prompt:
            headers += f"user_prompt: {user_prompt}\n"
            response = 'Response:\n' + resp
        if search_query:
            headers += f"search_query: {search_query}\n"
            response = 'Search Result:\n' + resp
        if link:
            headers += f"\nlink: {link}\n"
            response = response
        if not user_prompt and not search_query:
            response = resp
        self.strats['strat_tag'] = self.strat_tag
        self.strats['inputs'] = f"{headers}\n" + response
        self.strats['inputs_header'] = f"Text to clean:"
        return self.strats