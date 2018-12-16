import os

from libdlb.common import Params
from libdlb.common.utils import CONFIG_NAME

class Exp:
    def __init__(self,
                param_filepath: str,
                serialization_dir: str,
                overrides: str = ""):
        self.params = Params.from_file(param_filepath, overrides)
        self.serialization_dir = serialization_dir
        self.params.to_file(os.path.join(self.serialization_dir, CONFIG_NAME))

    def run(self):
        raise NotImplementedError
