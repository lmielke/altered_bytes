# data_labeled_df.py

from altered.yml_parser import YmlParser
import pandas as pd
pd.options.display.max_colwidth = 120

import altered.settings as sts
import altered.hlp_directories as hlp_dirs
import altered.hlp_printing as hlpp

class LabeledDataFrame:

    allowed_fields = {'columns'}

    def __init__(self, *args, **kwargs):
        self.fparser:object = YmlParser(*args, **kwargs)
        self.fields:dict = self.fparser(*args, **kwargs)
        self.dtypes:dict = {k: vs['type'] for k, vs in self.fields['meta'].items()}

    def __call__(self, *args, **kwargs):
        self.create_data_frame(*args, **kwargs)
        return self

    def 

    def create_data_frame(self, *args, **kwargs):
        self.data_frame = pd.LabeledDataFrame(columns=self.dtypes.keys()).astype(self.dtypes)
