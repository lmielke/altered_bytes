"""
# data_mtm.py
Stores mid term memory items such as system state and OS state.
"""

import os
from colorama import Fore, Style, Back

from altered.data_vectorized import VecDB
from altered.model_params import config as config
import altered.settings as sts
import altered.hlp_printing as hlpp


class Mtm(VecDB):
    """
    Manages Retrieval Augmentation Generation (RAG) data.
    """
    # default_data_dir handles where table data are stored and loaded
    default_data_dir = os.path.join(sts.resources_dir, 'mtm')
    # mtm_fields_path is the path to the fields file for the table creator
    mtm_fields_path = os.path.join(sts.data_dir, 'data_memory_required_fields.yml')

    def __init__(self, *args, name:str, u_fields_paths:list=[], **kwargs ):
        """Initializes the Mtm with the given model, setting up store and server connection.
        Args:
            model (str): The model name for generating embeddings.
        """
        u_fields_paths = self.load_mtm_fields(*args, u_fields_paths=u_fields_paths, **kwargs)
        super().__init__(*args, name=name, u_fields_paths=u_fields_paths, **kwargs, )

    def load_mtm_fields(self, *args, fields_paths:list=None, u_fields_paths:list=[], **kwargs):
        """
        Loads the fields for the Mtm from the given paths and extends it by
        whatever fields come from upstram objects such as search_engine.py
        these fielspaths will be used in VecDB to load these and additional fields
        """
        fields_paths = fields_paths if fields_paths is not None else [self.mtm_fields_path]
        fields_paths.extend(u_fields_paths)
        return fields_paths
       
    def __str__(self, *args, **kwargs):
        return f"Mtm(name={self.name}, fields=self.columns.keys(), )"