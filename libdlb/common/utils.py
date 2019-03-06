import os
import sys
import shutil
import importlib
import pkgutil
import pprint
import logging

import termcolor

from libdlb.common import Tqdm, TeeLogger

CONDA_ENV_CONFIG = 'conda-environment.yml'
CONFIG_NAME = 'config.json'
META_INFO_NAME = 'meta.json'
RESULT_NAME = 'result.json'
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

def mkdir_check(path: str, force=False):
    if os.path.exists(path):
        if not force:
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


def prepare_global_logging(serialization_dir: str, file_friendly_logging: bool) -> None:
    """
    This function configures 3 global logging attributes - streaming stdout and stderr
    to a file as well as the terminal, setting the formatting for the python logging
    library and setting the interval frequency for the Tqdm progress bar.
    Note that this function does not set the logging level, which is set in ``allennlp/run.py``.
    Parameters
    ----------
    serializezation_dir : ``str``, required.
        The directory to stream logs to.
    file_friendly_logging : ``bool``, required.
        Whether logs should clean the output to prevent carriage returns
        (used to update progress bars on a single terminal line). This
        option is typically only used if you are running in an environment
        without a terminal.
    """

    # If we don't have a terminal as stdout,
    # force tqdm to be nicer.
    if not sys.stdout.isatty():
        file_friendly_logging = True

    Tqdm.set_slower_interval(file_friendly_logging)
    std_out_file = os.path.join(serialization_dir, "stdout.log")
    sys.stdout = TeeLogger(std_out_file, # type: ignore
                           sys.stdout,
                           file_friendly_logging)
    sys.stderr = TeeLogger(os.path.join(serialization_dir, "stderr.log"), # type: ignore
                           sys.stderr,
                           file_friendly_logging)

    stdout_handler = logging.FileHandler(std_out_file)
    stdout_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
    logging.getLogger().addHandler(stdout_handler)
