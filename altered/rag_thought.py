"""
rag_thought.py
Combination of simple thought and rag_data to allow rag capabilities
"""
from colorama import Fore, Style

import altered.settings as sts
from altered.prompt import Prompt
from altered.rag_data import RAG_DB
from altered.thought import Thought


class RAG_Thought(Thought):
    mems_name = 'memories'

    def __init__(self, *args, name:str, **kwargs):
        # name of the thought can be used to locate/reference the saved thought
        self.name, self.thought_dir = self.mk_thought_dir(name, *args, **kwargs)
        # initial user_promt provided by the user
        self.init_user_prompt = None
        # prompt constructor for LLM interaction
        self.prompt = Prompt(*args, **kwargs)
        # Data represents the thought table structure, where each line is a thought element
        self.data = RAG_DB(*args, name=self.name, data_dir=self.thought_dir, **kwargs)
        # contains the references to all memories ever memoriezed
        self.mems = RAG_DB(*args, name=self.mems_name, data_dir=self.thought_dir, **kwargs)


    @property
    def memory(self, *args, **kwargs):
        return self.data.m_data

    @property
    def memories(self, *args, **kwargs):
        return self.mems.m_data

    def __call__(self, *args, **kwargs):
        self.run(*args, **kwargs)
        self.update_memories(*args, **kwargs)
        # self.mems.save_to_disk(*args, **kwargs)

    def update_memories(self, *args, **kwargs):
        # we retrieve the chat history from thought
        self.get_summary(*args, **kwargs)
        # self.mems.append(record, *args, **kwargs)
        # self.mems.save_to_disk(*args, **kwargs)

    def get_summary(self, *args, fmt:str=None, **kwargs):
        self.response = self.prompt(    *args,  
                                        user_prompt="Please write a summary of the ## Chat History.",
                                        fmt='plain',
                                        context=self.prep_context(*args, **kwargs), 
                                        **kwargs, 
                        )
        print(self.response)
        print(f"\n{self.response.get('response')}")
        

        
        
                