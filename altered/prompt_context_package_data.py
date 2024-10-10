"""
prompt_context_activities.py
"""

from colorama import Fore, Style

import altered.settings as sts
from altered.info_package_imports import PackageInfo
from altered.info_files import Tree

import os, subprocess, tomllib


class ContextPackageData:

    template_name = 'i_context_package_infos.md'
    trigger = 'package_infos'

    def __init__(self, *args, **kwargs):
        self.context = {}
        self.pg_data = PackageInfo(*args, **kwargs)
        self.tree = Tree(*args, **kwargs)

    def get_package_data(self, *args, **kwargs) -> dict:
        package_data = self.pg_data.analyze_package_imports(*args, show=False, **kwargs)
        return package_data

    def get_requirements(self, *args, pg_manager:str='pipenv', **kwargs) -> dict:
        """
        Gets installed libraries from the package.
        """
        if pg_manager == 'pipenv':
            req_format = 'Pipfile'
            requirements = self.load_from_pipenv(*args, **kwargs)
        elif pg_manager == 'pip':
            req_format = 'requirements.txt'
            requirements = self.load_from_pip(*args, **kwargs)
        return { 'requirements': requirements, 'req_format': req_format }

    def load_from_pipenv(self, *args, **kwargs) -> dict:
        """
        Load installed packages using Pipenv.
        """
        with open(os.path.join(sts.project_dir, 'Pipfile'), 'rb') as pipfile:
            return tomllib.load(pipfile)

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

    def mk_context(self, *args, package_infos: bool = False, **kwargs):
        if not package_infos:
            return {}
        self.context = {
                            'package_infos': self.get_package_data(*args, **kwargs),
        }
        self.context['package_infos'].update(self.get_requirements(*args, **kwargs))
        self.context['package_infos'].update(self.tree(*args, **kwargs))
        return self.context
