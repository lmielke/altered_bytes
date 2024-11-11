"""
prompt.py

"""
import os, yaml
from colorama import Fore, Style
from altered.renderer import Render
from altered.prompt_context import Context
from altered.prompt_instructs import Instructions
from altered.prompt_stats import PromptStats
from altered.model_connect import SingleModelConnect
from altered.prompt_deliverable import Deliverable
import altered.hlp_printing as hlpp
import altered.settings as sts

default_aggreg = 'default_user_prompt'


class Prompt:

    template_name = 'prompt.md'


    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.C = Context(name, *args, **kwargs)
        self.I = Instructions(name, *args, **kwargs)
        self.RD = Render(*args, **kwargs)
        self.stats = PromptStats(*args, **kwargs)
        self.delv = Deliverable(*args, **kwargs)
        self.data = None
        self.warnings = {}

    def __call__(self, *args, **kwargs):
        self.mk_prompt(*args, **kwargs)
        self.mk_prompt_summary(*args, **kwargs)
        self.data = self.render_prompt(*args, **kwargs)
        return self

    def mk_prompt(self, *args, verbose:int=0, **kwargs):
        """
        Constructs the final prompt as to be send to the AI model.
        """
        instructs = self.get_instructs(*args, verbose=verbose, **kwargs)
        user_prompt = instructs.get('user_prompt', {})
        del instructs['user_prompt']
        self.context = { 
                            'prompt_title': self.name,
                            'context': self.get_context(*args, verbose=verbose, **kwargs),
                            'deliverable': self.delv.mk_context(*args, **kwargs),
                            'user_comment': user_prompt,
                            'instructs': instructs,
                        }
        self.context['manifest'] = self.context.keys() - 'prompt_title'
        if verbose >= 2:
            print(self.stats(2, *args, data_dict=self.context, **kwargs))

    def render_prompt(self, *args, context:dict=None, _cont:dict=None, **kwargs):
        kwargs.update(self.get_template(*args, **kwargs))
        context = _cont if _cont is not None else self.context
        prompt = self.RD.render(*args, context=context, **kwargs, )
        hlpp.pretty_prompt(prompt, *args, **kwargs)
        return prompt

    def get_template(self, *args, template_name:str=None, **kwargs):
        if self.instructs.params.get('sub_method') == 'short':
            template_name = Instructions.template_name
        else:
            template_name = template_name if template_name is not None \
                                                                    else self.template_name
        if os.path.isfile(os.path.join(sts.templates_dir, template_name)):
            return {'template_name': template_name}
        else:
            print(  f"{Fore.YELLOW}WARNING: prompt.get_template: "
                    f"Template not found {Fore.RESET}, going with default "
                    f"'template_name': {self.template_name}")
            return {'template_name': self.template_name}

    def mk_prompt_summary(self, *args, context:dict=None, **kwargs):
        """
        prompt_summary can be used to create a short propmt for aggreation and other tasks
        """
        p_sum = {}
        if self.context['instructs'].get('user_prompt', {}).get('user_prompt') is not None:
            p_sum['question'] = self.context['instructs']['user_prompt']['user_prompt']
        else:
            p_sum['question'] = self.context['instructs']['strats'].get('description')
        p_sum['objective'] = (
                            f"{self.context['instructs']['strats'].get('objective')}\n"
                            f"{self.context['instructs']['strats'].get('your_task')}"
                                            )
        for k, v in p_sum.copy().items():
            p_sum[k] = v.replace("'<user_prompt>'", 'question')
        template = 'prompt_summary.md'
        _cont = {'prompt_summary': p_sum}
        self.context['prompt_summary'] = self.render_prompt(*args, _cont=_cont, **kwargs, )

    def get_context(self, *args, **kwargs):
        context_dict = self.C(*args, **kwargs)
        return context_dict

    def get_instructs(self, *args, **kwargs):
        self.instructs = self.I(*args, **kwargs)
        self.fmt = self.instructs.fmt
        return self.instructs.context


class Response:

    def __init__(self, name:str, *args, **kwargs):
        self.name = name
        self.r = {}
        self.v = Validations(name, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        checks_ok = self.v(*args, **kwargs)
        self.params_to_table(checks_ok, *args, **kwargs)
        if checks_ok:
            return self.extract(*args, **kwargs)
        else:
            return False

    def params_to_table(self, checks_ok, *args, **kwargs):
        kwargs['checks'] = checks_ok
        kwargs.update(self.v.validations)
        print(hlpp.dict_to_table('PROMPT kwargs', kwargs, *args, **kwargs))

    def extract(self, r:dict, *args, repeats:int=sts.repeats, **kwargs) -> dict:
        # r comes as a dictionary with 'results' containing a list of dictionaries
        if not r.get('responses') or type(r.get('responses')) != list:
            raise ValueError(f"Error: No valid responses returned from the AI model.")
        # we create the output record 
        record = {
                        'user_prompt': r.get('user_prompt'),
                        'role': 'assistant',
                        'model': r.get('model'),
                    }
        # r might have a single result or mulitple responses. We only return a single result.
        for i, result in enumerate(r.get('responses')):
            if result.get('strat_template') is not None:
                if result.get('strat_template') == repeats['agg']:
                    record.update(result)
                    break
        else:
            # if we did not find the aggregation result, we take the last result in r
            # in case there was only a single result, the single result is the last result
            record.update(result)
        record['content'] = record.get('response').strip()
        return record


from altered.prompt_strategies import Strategy
from collections import Counter
import json, yaml

class Validations(Prompt):

    ep = 'prompt.Validations ERROR: '  # error prefix
    error_file_name = '_errors.yml'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strats = Strategy(*args, **kwargs)
        self.errors = {}

    def __call__(self, r:dict, *args, **kwargs):
        self.errors = {}
        self.instruct_params = self.I.get_instruct_params(*args, **kwargs)
        self.strat_params, self.fmt = self.strats(*args, params=self.instruct_params, **kwargs)
        self.validations = self.strat_params.get('validations')
        self.validate(r, *args, **kwargs)
        self.error_tracking(*args, **kwargs)
        if self.errors:
            print(f"{Fore.RED}Response Validation Failed:{Fore.RESET}")
            return False
        else:
            print(f"{Fore.GREEN}Response Validation Passed{Fore.RESET}")
            return True

    def validate(self, r: dict, *args, **kwargs) -> dict:
        response = r.get('responses')[0].get('response').strip()
        self.resp_len_check(response, *args, **kwargs)
        self.resp_check_format(response, *args, **kwargs)
        self.resp_illegal_terms_check(response, *args, **kwargs)
        self.resp_illegal_ends_check(response, *args, **kwargs)
        self.resp_required_terms_check(response, *args, **kwargs)

    def resp_len_check(self, response, *args, **kwargs):
        if not response:
            self.msgs('Response Length', 'No response content returned from the AI model.')
        else:
            len_response = int(len(response) // self.strats.lpw)
        bias = 5
        if len_response < self.validations.get('expected_words')[0] - bias:
            self.msgs(  
                'Response Length', 
                f"Length: {len_response} < Min: {self.validations.get('expected_words')[0]}"
                )
        elif len_response > self.validations.get('expected_words')[1] + bias:
            self.msgs(
                'Response Length', 
                f"Length: {len_response} > Max: {self.validations.get('expected_words')[1]}"
                )

    def resp_check_format(self, response, *args, **kwargs):
        if self.fmt == 'json':
            try:
                r = json.loads(response)
            except json.JSONDecodeError as e:
                self.msgs('Response Format', f'JSON Decode Error: {e}')
        elif self.fmt == 'yaml':
            try:
                r = yaml.safe_load(response)
            except yaml.YAMLError as e:
                self.msgs('Response Format', f'YAML Error: {e}')
        elif self.fmt == 'makdown':
            pass

    def resp_illegal_terms_check(self, response, *args, **kwargs):
        num_inst_tags = response.count('<INST>')
        if num_inst_tags >= 2:
            self.msgs('Illegal Tags', f'Multiple <INST> tags found: Count {num_inst_tags}')
        illegal_terms = self.validations.get('illegal_terms')
        if not illegal_terms: return
        for il in illegal_terms:
            if il in response:
                self.msgs('Illegal Terms in response', f'{il} found')

    def resp_illegal_ends_check(self, response, *args, **kwargs):
        illegal_ends = self.validations.get('illegal_ends')
        if not illegal_ends: return
        resp_end = response[-100:]
        for il in illegal_ends:
            if il in resp_end:
                self.msgs('Promt Repitition Error', f'{il} found')

    def resp_required_terms_check(self, response, *args, **kwargs):
        required_terms = self.validations.get('required_terms')
        if not required_terms: return
        # required_terms indicate what constitutes a valid response
        for rq in required_terms:
            if rq not in response:
                self.msgs('Required Terms Missing', f'{rq} missing')

    def msgs(self, error_category: str, msg: str, *args, **kwargs):
        """
        Updates the errors Counter with structured error messages.

        Args:
            error_category (str): The category of the error.
            msg (str): The detailed error message.
        """
        if error_category not in self.errors:
            self.errors[error_category] = Counter()
        self.errors[error_category].update([msg])
        print(f"{Fore.RED}{self.ep}{Fore.RESET}{error_category}: {msg}")

    def error_tracking(self, *args, **kwargs):
        # if no errors were recorded, we return now
        if not self.errors:
            return

        # Load existing errors from the YAML file
        error_path = os.path.join(sts.strats_dir, self.error_file_name)
        if os.path.isfile(error_path):
            with open(error_path, 'r') as f:
                errors = yaml.safe_load(f) or {}
        else:
            errors = {}
        # Convert existing errors to nested Counter structure
        updated_errors = {}
        for category, messages in errors.get(self.strats.template_file_name, {}).items():
            updated_errors[category] = Counter(messages)

        # Merge existing errors with new errors
        for category, messages in self.errors.items():
            if category not in updated_errors:
                updated_errors[category] = messages
            else:
                updated_errors[category].update(messages)

        # Prepare the final dictionary structure to write back
        errors[self.strats.template_file_name] = {
            category: dict(messages) for category, messages in updated_errors.items()
        }

        # Write updated errors back to the YAML file
        with open(error_path, 'w') as f:
            yaml.safe_dump(errors, f)
