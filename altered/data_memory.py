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
    field_mappings = {
                        'teaser': {'title', }, 
                        'mgm_summary': {'short',}, 
                        'source': {'link', }
                        }

    def __init__(self, *args, name:str, u_fields_paths:list=[], data_file_name:str=None, 
                        **kwargs, 
        ):
        u_fields_paths = self.load_memory_fields(*args, u_fields_paths=u_fields_paths, **kwargs)
        super().__init__(*args, 
                            name=name, 
                            u_fields_paths=u_fields_paths, 
                            data_file_name=data_file_name if data_file_name is not None else \
                                                                        self.data_file_name,
                            **kwargs, 
                )
        self.temp_df = pd.DataFrame(columns=self.dtypes.keys(),)# dtypes=self.dtypes.values())

    def load_memory_fields(self, *args, fields_paths:list=None, u_fields_paths:list=[], **kwargs):
        """
        Loads the fields for the Memory from the given paths and extends it by
        whatever fields come from upstream objects such as search_engine.py
        these fields paths will be used in VecDB to load these and additional fields
        """
        fields_paths = fields_paths if fields_paths is not None else self.memory_fields_paths
        fields_paths.extend(u_fields_paths)
        return fields_paths

    def find_memories(self, memory_dir:str=None, *args, **kwargs):
        memories = []
        memory_dir = memory_dir if memory_dir is not None else sts.resources_dir
        for _dir, dirs, files in os.walk(memory_dir):
            for file in files:
                if file.endswith('.csv'):
                    memories.append(os.path.join(_dir, file))
        return memories

    def load_memories(self, memories:list, *args, **kwargs):
        print(f"load_memories.dtypes: {self.dtypes = }")
        for memory in memories:
            df = pd.read_csv(memory, delimiter=',')
            print(f"data_memory.load_memory: {Fore.YELLOW}{memory = }{Fore.RESET} \n{df}")
            
            # Filter df to include only columns present in self.temp_df
            filtered_df = df[self.temp_df.columns.intersection(df.columns)]
            
            # Map fields from filtered_df to align with temp_df using field_mappings
            mapped_df = filtered_df.rename(columns=self.get_mapped_fields())
            
            # Append the mapped DataFrame to self.temp_df
            self.temp_df = pd.concat([self.temp_df, mapped_df], ignore_index=True)
        print(self.temp_df)
        
    def get_mapped_fields(self):
        """
        Returns a dictionary that maps the fields in the input CSVs to the corresponding 
        fields in temp_df based on self.field_mappings
        """
        field_map = {}
        for key, values in self.field_mappings.items():
            for value in values:
                if value in self.temp_df.columns:
                    field_map[value] = key
        return field_map

    def __str__(self, *args, **kwargs):
        return f"Memory( name={self.name}, fields={list(self.temp_df.columns)}, )"

# Example usage:
# memory_instance = Memory(name="rag_memory")
# memories = memory_instance.find_memories()
# memory_instance.load_memories(memories)
# print(memory_instance.temp_df)