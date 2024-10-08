"""
prompt.py

"""
import os
from colorama import Fore, Style
from altered.renderer import Render
from altered.prompt_context import Context
from altered.prompt_instructs import Instructions
from altered.model_connect import SingleModelConnect
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
        self.data = None
        self.warnings = {}

    def __call__(self, *args, **kwargs):
        self.mk_prompt(*args, **kwargs)
        self.mk_prompt_summary(*args, **kwargs)
        self.data = self.render_prompt(*args, **kwargs)
        return self


    def mk_prompt(self, *args, **kwargs):
        """
        Constructs the final prompt as to be send to the AI model.
        """
        self.context = { 
                            'prompt_title': f"Prompt for {self.name}",
                            'context': self.get_context(*args, **kwargs),
                            'instructs': self.get_instructs(*args, **kwargs),
                        }

    def render_prompt(self, *args, context:dict=None, template_name:str=None, _context:dict=None, **kwargs):
        context = _context if _context is not None else self.context
        template_name = template_name if template_name is not None else self.template_name
        data = self.RD.render(*args, template_name=template_name, context=context, **kwargs, )
        hlpp.pretty_prompt(data, *args, **kwargs)
        return data

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
        _context = {'prompt_summary': p_sum}
        self.context['prompt_summary'] = self.render_prompt(*args, _context=_context,
                                                                    template_name=template, 
                                                                    **kwargs,
                                                                )

    def get_context(self, *args, **kwargs):
        context_dict = self.C(*args, **kwargs)
        return context_dict

    def get_instructs(self, *args, **kwargs):
        instructs = self.I(*args, **kwargs)
        return instructs


class Response:

    def __init__(self, *args, **kwargs):
        self.r = {}

    def __call__(self, *args, **kwargs):
        return self.extract(self.validate(*args, **kwargs), *args, **kwargs)

    def extract(self, r:dict, *args, repeats:int=sts.repeats, strat_templates:str=None, **kwargs) -> dict:
        print(f"{Fore.RED}{strat_templates = }{Fore.RESET}")
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
                if result.get('strat_template') == 'agg_std':#repeats['agg']:
                    record.update(result)
                    break
        else:
            # if we did not find the aggregation result, we take the last result in r
            # in case there was only a single result, the single result is the last result
            record.update(result)
        record['content'] = record.get('response').strip()
        return record


    @staticmethod
    def validate(r:dict, *args, **kwargs) -> dict:
        resp_content = r.get('responses')[0].get('response').strip()
        if not resp_content:
            raise ValueError(f"Error: No response content returned from the AI model.")
        if '</INST>' in resp_content:
            # content most likely contains the instruction tag which we remove here
            resp_content = resp_content.split('</INST>')
            if len(resp_content) > 2:
                raise ValueError(f"Error: Multiple Instruction Tags Found")
            elif len(resp_content) == 2:
                resp_content = resp_content[-1].strip()
        r['responses'][0]['response'] = resp_content
        return r
