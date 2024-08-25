import os
import subprocess

template = os.path.expanduser(r'~/python_venvs/libs/altered/altered/src/apis/serve.py')
executable = os.path.expanduser(r'~/.virtualenvs/altered-sg8orfNO/Scripts/python.exe')
workingdir = os.path.expanduser(r'~/python_venvs/libs/altered')

os.chdir(workingdir)
cmds = ['pipenv', 'run', 'python', template, 'serve', '-n', 'digiserver', '-rt', '-v', '2']
subprocess.Popen(cmds, shell=True)

# subprocess.call(['python', template, 'serve', '-n', 'digiserver', '-rt', '-v', '2'], shell=True,
#                 executable=executable)