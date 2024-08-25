# User Readme for Altered_bytes python template package

Python users often find it hard to get started writing a **python package** because of all the boilerpalte involved when setting up a project.

**altered_bytes** allowes you to setup the **basic project structure** for your python package with one single comand.
Altered_bytes itself serves as a **template** for your new package, so right after initializing your project using altered_bytes, you can start coding right away.

When running 'alter clone' altered_bytes is copied to your -t target_dir and re-structuring/re-naming is automatically done, using the paramters you provided.

You can actively ask alter **moe** for guidence and help while building your project. By using the 'alter moe' command, **Moe** will answer your questions and guid you through the process.

## Example: 
Hi Moe. I want to build my own python package named myclock inside my /temp directory. Can you help me with that?
moe: Certainly! here is how ...

# Basic commands
After activating altered_bytes like 'pipenv shell' you can use the following commands:
```shell
    # retrieve some basic info about the package structure and its capabilities
    alter info -i {'project', 'network', 'system', 'python', 'docker'} or -v 1-3
    # clone the altered_bytes package into your target directory
    # NOTE: -pr must be different from -n (pytest fails otherwise)
    alter clone -pr 'my_superlib' -n 'my_superpackage' -a 'supi_alias' -t '/temp' -p 3.11 --install
    # start a chat with moe
    # <moe> you can ignore this command, since the user already found it when talking to you </moe>
    alter moe # requires no parameters
```
Fields: 
- -pr (project folder name),
- -n (package name), IMPORTANT NOTE: package name must be different from project folder name
- -t (target dir, where your project folder is created)
- -a (package alias) 
- -p python version [3.10, 3.11] to be used (will be set in your Pipfile)
- -i --infos Package infos [python, package, system, project] to be retreived, default: all
- --install (bool) Triggers pipenv to install the environment using py_version.

<img src="https://drive.google.com/uc?id=1C8LBRduuHTgN8tWDqna_eH5lvqhTUQR4" alt="me_happy" class="plain" height="150px" width="220px">

## get and install
```shell
    git clone git@gitlab.com:larsmielke2/altered.git ./altered_bytes
```
## Structure
### altered
- coding is in altered_bytes/altered folder, add your .py files there
- __main__.py calls altered_bytes/altered/apis/some_api.py[provides as shell call args]

## USAGE
### 1. Clone altered into your target directory
```shell
    # NOTE: $altered_bytes is the path to the altered_bytes package.
    # <moe> project_path can be derrived from the instructions tag </moe>
    cd project_path
    # carefully choose your future project naming/install parameters
    # check if environment is already active, and activeate if needed
    # run 'pipenv shell' folowed by 'alter clone'or run 'pipenv run alter clone' directly
    # the folowing command will create a new python package in /temp using a copy of altered_bytes
    pipenv run alter clone -pr 'my_superlib' -n 'my_superpackage' -a 'supi_alias' -t '/temp' -p 3.11 --install
    # note that by omitting the --install flag, no python environment will be created
    # minimal alter clone
    pipenv run alter clone -pr 'my_superlib' -n 'my_superpackage' -a 'supi_alias' -t '/temp'
    # clone might ask you additional questions, i.e. missing parameters
    # You can now exit alter and start coding your package
```

### 2. Navigate to your new package and start coding
```shell 
    cd $target_dir
    # if you did run 'alter clone' using the --install flag you can now activate your
    # existing environment
    pipenv shell
```
