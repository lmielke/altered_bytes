import pandas as pd
from altered.yml_parser import YmlParser

class LabeledDataFrame(pd.DataFrame):
    
    @property
    def _constructor(self, *args, **kwargs):
        return LabeledDataFrame
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = YmlParser(*args, **kwargs)
        