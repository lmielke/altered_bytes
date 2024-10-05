# data_rag.py
import os
from colorama import Fore, Style, Back

from altered.data_vectorized import VecDB
from altered.model_params import config as config
import altered.settings as sts
import altered.hlp_printing as hlpp


class Rag(VecDB):
    """
    Manages Retrieval Augmentation Generation (RAG) data.
    """
    # default_data_dir handles where table data are stored and loaded
    default_data_dir = os.path.join(sts.resources_dir, 'rag')
    # rag_fields_path is the path to the fields file for the table creator
    rag_fields_paths = [
                        os.path.join(sts.data_dir, 'data_Rag_required_fields.yml'),
                        os.path.join(sts.data_dir, 'data_Stm_required_fields.yml'),
                        ]
    data_file_name = 'memory.csv'

    def __init__(self, *args, name:str, u_fields_paths:list=[], data_file_name:str=None, 
                        **kwargs, 
        ):
        """Initializes the Rag with the given model, setting up storage and server connection.
        Args:
            model (str): The model name for generating embeddings.
        """
        u_fields_paths = self.load_rag_fields(*args, u_fields_paths=u_fields_paths, **kwargs)
        super().__init__(*args, 
                            name=name, 
                            u_fields_paths=u_fields_paths, 
                            data_file_name=data_file_name if data_file_name is not None else \
                                                                        self.data_file_name,
                            **kwargs, 
                )

    def load_rag_fields(self, *args, fields_paths:list=None, u_fields_paths:list=[], **kwargs):
        """
        Loads the fields for the Rag from the given paths and extends it by
        whatever fields come from upstram objects such as search_engine.py
        these fielspaths will be used in VecDB to load these and additional fields
        """
        fields_paths = fields_paths if fields_paths is not None else self.rag_fields_paths
        fields_paths.extend(u_fields_paths)
        return fields_paths
       
    def __str__(self, *args, **kwargs):
        return f"Rag( name={self.name}, fields=self.columns.keys(), )"