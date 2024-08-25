# test_altered.py

import logging
import os
import unittest
import yaml

from altered.models.system import System
import altered.settings as sts
from altered.helpers.function_to_json import FunctionToJson
f_json = FunctionToJson()



class Test_System(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verbose = 0
        cls.testData = cls.mk_test_data()
        cls.content = """
                                Certainly! To create your package named `myclocklib` in your temp directory, run the following command in your terminal:  ```shell pipenv run alter clone -pr 'myclock' -n 'myclock' -a 'clock' -t 'C:\\temp' -p 3.11 --install ```  \nThis will clone `altered_bytes` to `C:/Users/lars/myclock`, set up the environment, and install dependencies.
                            """
        cls.code_blocks = """
            You can list all files in the current directory using the `ls` command on Unix-
           like systems or the `dir` command on Windows. Since you're using Windows, you
           can use the following command in your shell:

           ```shell

           dir

           ```

           If you want to list the files in a format similar to Unix systems, you can use:

           ```shell

           dir /B

           ```
        """

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def mk_test_data(cls):
        with open(os.path.join(sts.test_data_dir, "test_altered.yml"), "r") as f:
            return yaml.safe_load(f)



    def test_get_code_blocks(self):
        system = System()
        code_blocks = system.get_code_blocks({'content': self.code_blocks})
        # print(f"\n{sts.YELLOW}\nCode blocks: {code_blocks}{sts.RESET}")


    def test_execute(self):
        system = System()
        codes = [f"pipenv run alter info", f"dir", 'dir /AD', 'ls -la']
        system.commands = [{
                            'indicator': '```', 'language': 'shell', 
                            'code': (codes[1]), 
                            'user_confirmed_execution': False
                            }]
        # out = system.confirm_and_run()
        out = system.execute()
        # print(system.comunicate(verbose=1))

    @f_json.open_ai_function(apis={"open_ai_api_",}, write=True,)
    def test_adhog_assist_shell_action(self):
        system = System()
        cmds = [
                "dir", 
                "alter clone -pr 'myhammerlib' -n 'myhammer' -a 'myham' -t 'C:/temp' -p '3.10' --install -y"
                ]
        out = system.adhog_assist_shell_action(cmds[0], exec='shell')
        # print(f"test_adhog_assist_shell_action: {out}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
