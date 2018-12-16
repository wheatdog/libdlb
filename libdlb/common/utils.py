import os
import sys
import shutil
import importlib
import pkgutil
import pprint

import termcolor

CONDA_ENV_CONFIG = 'conda-environment.yml'
CONFIG_NAME = 'config.json'
SRC_DIR = 'src'

def import_submodules(package_name: str) -> None:
    """
    Import all submodules under the given package.
    Primarily useful so that people using AllenNLP as a library
    can specify their own custom packages and have their custom
    classes get loaded and registered.
    """
    importlib.invalidate_caches()

    new_modules = []

    # Import at top level
    module = importlib.import_module(package_name)
    new_modules.append(module)
    path = getattr(module, '__path__', [])
    path_string = '' if not path else path[0]

    # walk_packages only finds immediate children, so need to recurse.
    for module_finder, name, _ in pkgutil.walk_packages(path):
        # Sometimes when you import third-party libraries that are on your path,
        # `pkgutil.walk_packages` returns those too, so we need to skip them.
        if path_string and module_finder.path != path_string:
            continue
        subpackage = f"{package_name}.{name}"
        new_modules.extend(import_submodules(subpackage))

    return new_modules

def mkdir_check(path: str):
    if os.path.exists(path):
        text = termcolor.colored('{} exists. Do you want to remove the existing directory and proceed? [type n to stop]'.format(path), 'red')
        print(text, file=sys.stderr)
        answer = input()
        if answer == 'n':
            exit()
        shutil.rmtree(path)
    os.makedirs(path)

def conda_env_export(filepath):
    try:
        import subprocess
        env_info = subprocess.check_output('conda env export', shell=True)
        env_info = env_info.decode()
        with open(filepath, 'w') as f:
            print(env_info, file=f, end='')
    except OSError as e:
        print(e)

class FormatPrinter(pprint.PrettyPrinter):
    def __init__(self, formats):
        super(FormatPrinter, self).__init__()
        self.formats = formats

    def format(self, obj, ctx, maxlvl, lvl):
        if type(obj) in self.formats:
            return self.formats[type(obj)](obj), 1, 0
        return pprint.PrettyPrinter.format(self, obj, ctx, maxlvl, lvl)
