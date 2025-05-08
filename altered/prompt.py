"""
prompt.py

"""
import os, time, yaml
from colorama import Fore, Style
from altered.renderer import Render
from altered.prompt_context import Context
from altered.prompt_user_prompt import UserPrompt
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
        self.U = UserPrompt(*args, **kwargs)
        self.I = Instructions(name, *args, **kwargs)
        self.RD = Render(*args, **kwargs)
        self.stats = PromptStats(*args, **kwargs)
        self.D = Deliverable(*args, **kwargs)
        self.data = None # contains the rendered prompt
        self.warnings = {}
        self.context = {} # contains the context for rendering the prompt

    @sts.logs_timeit.timed("prompt.Prompt.__call__")
    def __call__(self, *args, **kwargs):
        self.get_context(*args, **kwargs)
        self.get_deliverable(*args, **kwargs)
        self.get_user_prompt(*args, **kwargs)
        self.get_instructs(*args, **kwargs)
        self.mk_prompt(*args, **kwargs)
        self.mk_prompt_summary(*args, **kwargs)
        self.data = self.render_prompt(*args, **kwargs)
        return self

    def mk_prompt(self, *args, verbose:int=0, **kwargs):
        """
        Constructs the final prompt as to be send to the AI model.
        """
        # user_prompt = self.user_prompt
        # line removed because serves no appearent purpose, delete if no issues
        # del self.instructs.context['user_prompt']
        self.context = { 
                            'prompt_title': self.name,
                            'context': self.context_dict,
                            'deliverable': self.deliverable,
                            'user_comment': self.up,
                            'instructs': self.instructs.context,
                        }
        self.context['manifest'] = self.context.keys() - 'prompt_title'
        if verbose >= 2:
            print(f"\n{Fore.CYAN}Prompt.mk_prompt.context:{Fore.RESET} {verbose = } >= 2")
            print(self.stats(2, *args, data_dict=self.context, **kwargs))

    def render_prompt(self, *args, context:dict=None, _cont:dict=None, verbose:int=0, **kwargs
        ):
        kwargs.update(self.get_template(*args, **kwargs))
        context = _cont if _cont is not None else self.context
        prompt = self.RD.render(*args, context=context, **kwargs, )
        if verbose >= 1:
            print(f"\n{Fore.CYAN}Prompt.render_prompt.prompt:{Fore.RESET} {verbose = } >= 1")
            hlpp.pretty_prompt(prompt, *args, verbose=verbose, **kwargs)
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
        self.context_dict = self.C(*args, **kwargs)

    def get_deliverable(self, *args, **kwargs):
        self.deliverable = self.D.mk_context(*args, **kwargs)
        # self.deliverable = {'content': 'this is a test', }

    def get_user_prompt(self, *args, strat_template:str=None, **kwargs):
        self.up = UserPrompt(*args, **kwargs)(*args, **kwargs)
        if strat_template is None and self.up.get('user_prompt') is None:
            print(f"{Fore.RED}ERROR:{Fore.RESET} default strat requires a user_prompt")
            self.up = UserPrompt(*args, **kwargs)(*args, user_prompt='', **kwargs)
        self.user_prompt = self.up.get('user_prompt')

    def get_instructs(self, *args, user_prompt:str=None, **kwargs):
        self.instructs = self.I(*args, user_prompt=self.user_prompt, **kwargs)
        self.instructs.context['inputs'] = self.get_inputs(*args, **kwargs)
        self.fmt = self.instructs.fmt

    def get_inputs(self, *args, **kwargs):
        if self.deliverable.get('content') and not self.up.get('user_prompt'):
            return "'<deliverable>'"
        elif not self.deliverable.get('content') and self.up.get('user_prompt'):
            return "'<user_comment>'"
        elif self.deliverable.get('content') and self.up.get('user_prompt'):
            return "'<user_comment>' and '<deliverable>'"
        # there must be some sort of input for the LLM to work with
        elif not self.deliverable.get('content') and not self.up.get('user_prompt'):
            raise ValueError(f"{Fore.RED}ERROR:{Fore.RESET} No inputs found")



class Response:

    def __init__(self, name:str, *args, **kwargs):
        self.name = name
        self.r = {}
        self.V = Validations(name, *args, **kwargs)

    @sts.logs_timeit.timed("prompt.Response.__call__")
    def __call__(self, *args, **kwargs):
        checks_ok = self.V(*args, **kwargs)
        self.params_to_table(checks_ok, *args, **kwargs)
        if checks_ok:
            extracted = self.extract(*args, **kwargs)
            return extracted
        else:
            return False

    def params_to_table(self, checks_ok, *args, verbose:int=0, **kwargs):
        kwargs['checks'] = checks_ok
        kwargs.update(self.V.validations)
        if verbose:
            print(hlpp.dict_to_table('Response.params_to_table.kwargs', kwargs, *args, **kwargs))

    def extract(self, r:dict, *args, repeats:int=sts.repeats, **kwargs) -> dict:
        # r comes as a dictionary with 'results' containing a list of dictionaries
        if not r.get('responses') or type(r.get('responses')) != list:
            raise ValueError(f"Error: No valid responses returned from the AI model.")
        # we create the output record 
        record = {
                        'user_prompt': r.get('user_prompt'),
                        'role': 'assistant',
                        'model': r.get('model'),
                        'content': None,
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

    @sts.logs_timeit.timed("prompt.Validations.__call__")
    def __call__(self, r:dict, *args, verbose:int=0, **kwargs):
        self.errors = {}
        self.instruct_params = self.I.get_instruct_params(*args, **kwargs)
        self.strat_params, self.fmt = self.strats(*args, params=self.instruct_params, **kwargs)
        self.validations = self.strat_params.get('validations')
        self.validate(r, *args, verbose=verbose, **kwargs)
        self.error_tracking(*args, **kwargs)
        if verbose:
            print(f"{Fore.CYAN}\nprompt.Validations.__call__.response:{Fore.RESET}", end=' ')
        if self.errors:
            print(f"\n{Fore.RED}ERROR: {r['responses'][0].get('response') = }{Fore.RESET}\n")
            return False
        else:
            if verbose:
                print(f"{Fore.GREEN}OK{Fore.RESET}")
            return True

    def validate(self, *args, verbose:int=1, **kwargs) -> dict:
        response = self.get_response(*args, **kwargs)
        if not response:
            return
        if not self.strat_params.get('validations'):
            if verbose:
                print(f"{Fore.YELLOW}No validations found{Fore.RESET}")
            return
        self.resp_len_check(response, *args, **kwargs)
        self.resp_check_format(response, *args, **kwargs)
        self.resp_illegal_terms_check(response, *args, **kwargs)
        self.resp_illegal_ends_check(response, *args, **kwargs)
        self.resp_required_terms_check(response, *args, **kwargs)

    def get_response(self, r:dict, *args, **kwargs):
        response = r.get('responses')[0].get('response')
        if not response:
            self.msgs('Response Length', 'No response content returned from the AI model.')
            return False
        else:
            return response

    def resp_len_check(self, response, *args, **kwargs):
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
