import os
import warnings
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, List
from colorama import Fore, Style

import altered.settings as sts
from altered.yml_parser import YmlParser

from altered.prompt_strats_fields import StrategyFields


class Strategy:

    inputs_tag = 'input_data'
    template_name = 'i_instructs_strats.md'


    def __init__(self, *args, **kwargs):
        self.fields = None
        self.templates = {}
        self.s_type = None
        self.s_name = None
        self.fmt = None
        self.template_name = None
        self.template_file_name = None
        self.template_path = None

    def __call__(self, *args, **kwargs):
        self.mk_strat_params(*args, **kwargs)
        self.load_strat(*args, **kwargs)
        self.strat_input_data = self.get_strat_input_data(*args, **kwargs)
        self.set_validation_params(*args, **kwargs)
        return self.fields.__dict__, self.fmt

    def set_validation_params(self, *args, **kwargs):
        self.validations['inputs_len'] = len(self.strat_input_data) if self.strat_input_data \
                                                                                        else 0
        lengths, self.lpw = self.validations['expected_len'], 4
        self.validations['expected_words'] = (   
                            int(self.validations['inputs_len'] * lengths[0]) // self.lpw,
                            int(self.validations['inputs_len'] * lengths[1]) // self.lpw,
                        )

    def mk_strat_params(self, strat_template_name: str, *args, **kwargs):
        self.template_name = strat_template_name
        self.template_file_name = f'{strat_template_name}.yml'
        self.template_path = os.path.join(sts.strats_dir, self.template_file_name)
        self.s_type, s_meth = strat_template_name.split('_', 1)
        self.fields = StrategyFields(s_meth=s_meth, s_type=self.s_type)

    def load_strat(self, *args, fmt='markdown', **kwargs):
        loader = YmlParser(*args, fields_paths=[self.template_path], **kwargs)
        self.fmt = loader.data.get('fmt', fmt)
        self.fields.strats_method = {
                                        'body': loader.describe(fmt=fmt),
                                        'meta': loader.fields.get('meta'),
        }
        for k, vs in loader.data.items():
            if k in {'validatins'}: continue
            setattr(self.fields, k, vs)
        setattr(self, 'validations', loader.data.get('validations'))

    def mk_context(self, *args, **kwargs):
        return self.fields.__dict__

    # def add_strat(self, s_meth, value):
    #     setattr(self.fields, s_meth, value)
    #     self.fields.__post_init__()

    def get_strat_input_data(self, *args, strat_input_data:str=None, **kwargs):
        """
        Strats can be provided with a generic strat_input_data:str field.
        strat_input_data can be the data itself or it can be a link to a data source.
        This method gets the data and assigns it to a self.input_data field.
        """
        if strat_input_data is None:
            return None
        else:
            return strat_input_data


class Default(Strategy):
    pass


class Agg(Strategy):
    inputs_tag = 'sample'

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        strat = self.mk_prompt_agg_instruct(*args, **kwargs)
        self.fields.check_values(*args, **kwargs)
        return strat, self.fmt

    def check_params(self, responses:List[str], template_name:str, *args, **kwargs):
        if not responses:
            msg = ( f"{Fore.RED}prompt_strategies.Agg: No texts provided"
                    f" to aggregate. {Style.RESET_ALL} {template_name = }, {responses = }"
                    )
            raise ValueError(msg)

    def mk_prompt_agg_instruct(self, *args, responses:List[str]=None, **kwargs) -> dict:
        self.check_params(responses, *args, **kwargs)
        self.fields.inputs_tag = self.inputs_tag
        self.fields.inputs_intro = (
            f"Below is the {self.inputs_tag} of {len(responses)} different texts, "
        )
        
        if not kwargs.get('prompts'):
            self.fields.inputs_intro += (
                f"that need to be aggregated. "
                f"Note, that there is no 'prompt' associated with these responses. "
                f"Therefore you have to infer the 'prompt' from other information, "
                f"i.e. the responses, name or search query."
            )
            self.fields.inputs_header = f"Texts to aggregate:"
            self.fields.inputs_data = self.mk_sample_no_prompt(*args, responses=responses, 
                                                                                    **kwargs)
        elif len(kwargs['prompts']) == 1:
            self.fields.inputs_header = f"Answers to a single prompt:"
            self.fields.inputs_intro += f"trying to answer the same single prompt."
            self.fields.inputs_data = self.mk_sample_single_prompt(*args, responses=responses,
                                                                                    **kwargs)
        elif len(kwargs['prompts']) > 1:
            self.fields.inputs_header = f"Answers and prompts:"
            self.fields.inputs_intro += f"trying to answer {len(kwargs['prompts'])} prompts."
            self.fields.inputs_data = self.mk_sample_multi_prompt(*args, responses=responses, 
                                                                                    **kwargs)
        else:
            self.fields.inputs_data = self.mk_sample_no_prompt(*args, responses=responses, 
                                                                                    **kwargs)
        
        return self.fields.__dict__

    def mk_sample_multi_prompt(self, *args, prompts: List[str], responses: List[str], 
        rm_tags: bool = False, **kwargs) -> str:
        sample_pairs = []
        for i, (prompt, resp) in enumerate(zip(prompts, responses)):
            if rm_tags:
                prompt = self.rm_tags(prompt, *args, **kwargs)
            sample_pairs.append(
                f"\n__SAMPLE {i+1}__\n\n"
                f"Prompt {i+1}: {prompt}\n"
                f"Response {i+1}: {resp}"
            )
        all_samples = '\n\n'.join(sample_pairs)
        return f"Samples of Provided multiple Prompts and Answers:\n{all_samples}\n"

    def mk_sample_single_prompt(self, *args, prompts: List[str], responses: List[str], 
        rm_tags: bool = False, **kwargs) -> str:
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
        all_samples = '\n'.join(samples)
        return (
            f"\nOriginal Prompt for all Samples:\n{prompt}\n"
            f"Samples of Provided Answers to the Original Prompt:\n{all_samples}\n"
        )

    def mk_sample_no_prompt(self, *args, responses: List[str], **kwargs) -> str:
        samples = []
        for i, response in enumerate(responses):
            samples.append(
                f"\n__TEXT SAMPLE {i+1}__\n"
                f"{response}"
            )
        all_samples = '\n'.join(samples)
        return f"Samples of Provided Texts:\n{all_samples}\n"

    def rm_tags(self, prompt: str, *args, **kwargs) -> str:
        tags = ['context', 'user_prompt', 'sample', 'io_template', 'INST']
        for tag in tags:
            prompt = prompt.replace(f"<{tag}>", "").replace(f"</{tag}>", "")
        return prompt

class Format(Strategy):

    inputs_tag = 'unformatted_text'
    header = 'Unformatted Text'
    intro = f'Below is a {inputs_tag} that needs to be formatted.'

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        strat = self.mk_strat_fields(*args, **kwargs)
        self.fields.check_values(*args, **kwargs)
        return strat, self.fmt

    def mk_strat_fields(self, *args, **kwargs) -> dict:
        self.fields.inputs_tag = self.inputs_tag
        self.fields.expected_words = self.validations['expected_words']
        self.fields.inputs_data = f"{self.strat_input_data}"
        self.fields.inputs_header = self.header
        self.fields.inputs_intro = self.intro
        return self.fields.__dict__

class Clean(Strategy):

    inputs_tag = 'poluted_text'

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        strat = self.mk_prompt_reduce_instruct(*args, **kwargs)
        self.fields.check_values(*args, **kwargs)
        return strat, self.fmt

    def mk_prompt_reduce_instruct(self, *args, 
                                  strat_input_data: List[str],
                                  user_prompt: Optional[str] = None,
                                  link: Optional[str] = None,
                                  rm_tags: bool = False,
                                  search_query: Optional[str] = None, 
                                  **kwargs) -> dict:
        headers = ''
        if user_prompt:
            headers += f"user_prompt: {user_prompt}\n"
            response = 'Response:\n' + strat_input_data
        if search_query:
            headers += f"search_query: {search_query}\n"
            response = 'Text:\n' + strat_input_data
        if link:
            headers += f"\nlink: {link}\n"
            response = response
        if not user_prompt and not search_query:
            response = strat_input_data
        
        self.fields.inputs_tag = self.inputs_tag
        self.fields.expected_words = self.expected_words
        self.fields.inputs_len = inputs_len
        self.fields.inputs_data = f"{headers}\n" + response
        self.fields.inputs_header = f"Text to Clean:"
        self.fields.inputs_intro = (
                                        f"Below is a {self.inputs_tag}, that needs to be "
                                        f"cleaned and summarized.")
        return self.fields.__dict__
