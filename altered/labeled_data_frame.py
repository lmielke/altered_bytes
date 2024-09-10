import pandas as pd
from altered.yml_parser import YmlParser

class LabeledDataFrame(pd.DataFrame):
    """
    Allows to label the df columns with loaded labels from a YAML fields file.
    labels can be added like:
    df.fields.add_labels(name='Unittest', labels=fields_path.yml, description="Test DF")
    Then the labels can be accessed like:
    df.fields.describe() or simply df.fields()
    also the output format can be specified like:
    df.fields.describe(fmt='tbl/json/yml') 
    """
    
    @property
    def _constructor(self, *args, **kwargs):
        return LabeledDataFrame
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = YmlParser(*args, **kwargs)
        