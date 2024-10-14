# data_memory.py
import csv, os, re
from colorama import Fore, Style, Back
import pandas as pd
from altered.data_vectorized import VecDB
from altered.model_params import config as config
import altered.settings as sts
import altered.hlp_printing as hlpp


class Memory(VecDB):
    """
    Manages Retrieval Augmentation Generation (RAG) data.
    """
    # default_data_dir handles where table data are stored and loaded
    default_data_dir = os.path.join(sts.resources_dir, 'memory')
    # memory_fields_path is the path to the fields file for the table creator
    memory_fields_paths = [os.path.join(sts.data_dir, 'data_memory_required_fields.yml'), ]
    data_file_name = 'memory.csv'

    def __init__(self, *args, name:str, u_fields_paths:list=[], data_file_name:str=None, 
                        **kwargs, 
        ):
        """Initializes the Memory with the given model, setting up stomemorye and server connection.
        Args:
            model (str): The model name for generating embeddings.
        """
        u_fields_paths = self.load_memory_fields(*args, u_fields_paths=u_fields_paths, **kwargs)
        super().__init__(*args, 
                            name=name, 
                            u_fields_paths=u_fields_paths, 
                            data_file_name=data_file_name if data_file_name is not None else \
                                                                        self.data_file_name,
                            **kwargs, 
                )

    def load_memory_fields(self, *args, fields_paths:list=None, u_fields_paths:list=[], **kwargs):
        """
        Loads the fields for the Memory from the given paths and extends it by
        whatever fields come from upstram objects such as search_engine.py
        these fielspaths will be used in VecDB to load these and additional fields
        """
        fields_paths = fields_paths if fields_paths is not None else self.memory_fields_paths
        fields_paths.extend(u_fields_paths)
        return fields_paths

    def find_memories(self, memory_path:str=None, *args, **kwargs):
        memories = []
        memory_path = memory_path if memory_path is not None else sts.resources_dir
        for _dir, dirs, files in os.walk(memory_path):
            for file in files:
                if file.endswith('.csv'):
                    memories.append(os.path.join(_dir, file))
        return memories

    def load_memories(self, memories:list, *args, **kwargs):
        for memory in memories:
            # use dtype category to reduce df size
            # see https://www.youtube.com/watch?v=RlIiVeig3hc (7:30)
            # NOTE: when reading from bit.ly, no additional parameter are needed !
            # bit.ly/imdbratings, chiporders, smallstocks, kaggletrain, uforeports
            df = pd.read_csv(memory, delimiter=',', )
            print(f"data_memory.load_memory: {Fore.YELLOW}{memory = }{Fore.RESET} \n{df}")
        
       
    def __str__(self, *args, **kwargs):
        return f"Memory( name={self.name}, fields=self.columns.keys(), )"