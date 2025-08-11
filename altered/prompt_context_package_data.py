"""
prompt_context_package_data.py
"""

from colorama import Fore, Style

from altered.info_package_imports import PackageInfo
from altered.info_files import Tree

import os, subprocess, tomllib


class ContextPackageData:

    template_name = 'i_context_package_info.md'
    trigger = 'package_info'

    def __init__(self, *args, **kwargs):
        self.context = {}
        self.data = PackageInfo(*args, **kwargs)
        self.tree = Tree(*args, **kwargs)

    def get_pg_imports(self, *args, work_file_name:str=None, **kwargs) -> dict:
        if work_file_name is None:
            return {}
        data = self.data.analyze_package_imports(*args, 
                                                        work_file_name=work_file_name,
                                                        show=False, **kwargs
                    )
        if data.get('digraph'):
            data['digraph'] = '\n'.join([line.split('[')[0] for line in 
                    data.get('digraph', '').split('\n') if 'fillcolor' not in line])
        return data

    def get_requirements(self, *args, pg_manager:str='pipenv', **kwargs) -> dict:
        """
        Gets installed libraries from the package.
        """
        if pg_manager == 'pipenv':
            req_format = 'Pipfile'
            pg_requirements = self.load_from_pipenv(*args, **kwargs)
        elif pg_manager == 'pip':
            req_format = 'requirements.txt'
            pg_requirements = self.load_from_pip(*args, **kwargs)
        return { 'pg_requirements': pg_requirements, 'req_format': req_format }

    def load_from_pipenv(self, *args, project_dir:str, **kwargs) -> dict:
        """
        Load installed packages using Pipenv.
        """
        with open(os.path.join(project_dir, 'Pipfile'), 'rb') as f:
            return f.read()

    def load_from_pip(self, *args, **kwargs) -> dict:
        """
        Load installed packages using Pip.
        """
        try:
            result = subprocess.run(
                ['pip', 'freeze'],
                capture_output=True,
                text=True,
                check=True
            )
            installed_packages = result.stdout.splitlines()
            return {pkg.split('==')[0]: pkg.split('==')[1] for pkg in installed_packages if '==' in pkg}
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error fetching pip requirements: {e.stderr}" + Style.RESET_ALL)
            return {}

    def mk_context(self, *args,     package_info:bool=False,
                                    is_package:bool=False,
                                    pg_imports:bool=False, 
                                    pg_requirements:bool=False, 
                                    pg_tree:bool=False,
                                    verbose:int=0,
        **kwargs) -> dict:
        if verbose:
            print(f"{Fore.YELLOW}ContextPackageData.mk_context{Fore.RESET} {package_info = }")
        if not package_info: return {}
        # Note: there are additional flags to get various package_infos
        self.context['package_info'] = {'is_package': is_package, }
        if pg_imports and is_package:
            try:
                self.context['package_info'].update(self.get_pg_imports(*args, **kwargs))
                if verbose:
                    print(f"{Fore.YELLOW}\tpg_imports: {Fore.RESET} {pg_imports}")
            except Exception as e:
                print(f"{Fore.RED}Error getting package imports: {e}{Fore.RESET}")
                self.context['package_info']['pg_imports'] = {'Imports': 'Not found'}
        if pg_requirements and is_package:
            self.context['package_info'].update(self.get_requirements(*args, **kwargs))
            if verbose:
                print(f"{Fore.YELLOW}\tpg_requirements: {Fore.RESET} {pg_requirements}")
        if pg_tree:
            self.context['package_info'].update(self.tree(*args, **kwargs))
            if verbose:
                print(f"{Fore.YELLOW}\tpg_tree: {Fore.RESET} {pg_tree}")
        return self.context
