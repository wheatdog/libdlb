import os
import sys
import argparse
from shutil import copy

from libdlb.common.utils import mkdir_check, import_submodules, conda_env_export, CONDA_ENV_CONFIG, SRC_DIR
from libdlb.exp import Exp

def local_mod_src_preserve(new_base, added_modules):
    files = []

    # TODO: now assume user script modules are in cwd
    cwd = os.getcwd()
    for mod in added_modules:
        filepath = mod.__file__
        if filepath is None:
            continue
        filepath = os.path.realpath(filepath)
        if filepath.startswith(cwd):
            files.append(filepath)

    for filepath in files:
        new_filepath = filepath.replace(cwd, new_base)
        os.makedirs(os.path.dirname(new_filepath), exist_ok=True)
        copy(filepath, new_filepath)
        print(filepath, '-->', new_filepath)

def main():
    parser = argparse.ArgumentParser(
        description="Universal Experiment Wrapper",
        usage='%(prog)s',
        prog='libdlb-run')

    parser.add_argument('param_path',
                        type=str,
                        help='path to parameter file describing the model to be trained')

    parser.add_argument('-e', '--experiment-class',
                        required=True,
                        type=str,
                        help='the name of experiment class implemented in additional packages')

    parser.add_argument('-s', '--serialization-dir',
                        required=True,
                        type=str,
                        help='directory in which to save the model and its logs')

    parser.add_argument('-o', '--overrides',
                        type=str,
                        default="",
                        help='override configuration')

    parser.add_argument('-i', '--include-package',
                        required=True,
                        type=str,
                        action='append',
                        default=[],
                        help='additional packages to include')

    args = parser.parse_args()

    added_modules = []
    for package_name in getattr(args, 'include_package', ()):
        added_modules.extend(import_submodules(package_name))

    # Find the experiment class
    exp_cls = None
    for mod in added_modules:
        result = getattr(mod, args.experiment_class, None)
        if result and issubclass(result, Exp):
            exp_cls = result
            break

    mkdir_check(args.serialization_dir)

    local_mod_src_preserve(os.path.join(args.serialization_dir, SRC_DIR), added_modules)

    conda_env_export(os.path.join(args.serialization_dir, CONDA_ENV_CONFIG))

    exp_cls(args.param_path, args.serialization_dir, args.overrides).run()

if __name__ == '__main__':
    main()
