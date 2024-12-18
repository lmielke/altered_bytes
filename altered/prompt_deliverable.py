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

    def get_context_info(self, *args,   deliverable_path:str=None, 
                                        selection:str=None, **kwargs,
        ) -> dict:
        """
        Get the content of the deliverable file. This can be code or any kind of text.
        """
        if deliverable_path is not None:
            with open(deliverable_path, 'r') as f:
                self.deliverable = f.read()
        if selection is not None:
            self.selection += "Note: "
            if selection in self.deliverable:
                self.selection += f"This section was highlighted from above deliverable. \n\n"
                selection = f"```\n\n{selection}\n\n```"
            else:
                pass
            self.selection += selection

    def mk_context(self, *args, deliverable_path:str=None, **kwargs):
        """
        This context dict contains variables to be rendered in a jinja template.
        """
        if deliverable_path is None: return {}
        self.get_context_info(*args, deliverable_path=deliverable_path, **kwargs)
        if self.deliverable:
            self.context['content'] = self.deliverable
            self.context['selection'] = self.selection
        return self.context

