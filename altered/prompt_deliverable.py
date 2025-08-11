"""
prompt_deliverable.py
"""

from colorama import Fore, Style
import altered.settings as sts


class Deliverable:

    template_name = 'i_deliverable.md'
    trigger = 'deliverable'

    def __init__(self, *args, **kwargs):
        self.deliverable, self.selection = '', ''
        self.context = {}

    def get_context_info(self, *args, deliverable_path:str=None, **kwargs, 
        ) -> dict:
        """
        Get the content of the deliverable file. This can be code or any kind of text.
        """
        if deliverable_path is None: return
        with open(deliverable_path, 'r', encoding="utf-8") as f:
            self.deliverable = f.read()
        # if selection is not None:
        #     if selection in self.deliverable:
        #         selection = f"```\n\n{selection}\n\n```"
        #     else:
        #         pass
        #     self.selection += selection

    def mk_context(self, *args, selection:str=None, **kwargs):
        """
        This context dict contains variables to be rendered in a jinja template.
        """
        self.get_context_info(*args, **kwargs)
        if self.deliverable:
            self.context['content'] = self.deliverable
        if selection:
            self.context['selection'] = f"```\n{selection}\n```"
        return self.context

