import os

from typing import Any, Dict, List
from libdlb.common import Params
from libdlb.common.utils import CONFIG_NAME, META_INFO_NAME, RESULT_NAME

class Exp:
    def __init__(self,
                 params,
                 serialization_dir: str,
                 meta_info=None):
        assert isinstance(params, Params) or isinstance(params, dict)
        if isinstance(params, Params):
            self.params = params
        else:
            self.params = Params(params)

        if isinstance(meta_info, Params):
            self.meta_info = meta_info
        else:
            self.meta_info = Params(meta_info)

        self.serialization_dir = serialization_dir
        self.params.to_file(os.path.join(self.serialization_dir, CONFIG_NAME))
        self.meta_info.to_file(os.path.join(self.serialization_dir, META_INFO_NAME))
        self.result = {}
        self._prepare()

    def _prepare(self):
        pass

    def run(self):
        raise NotImplementedError

    def post_process(self):
        import json
        report_string = json.dumps(self.result, sort_keys=True, indent=4, separators=(',', ': '))
        print(report_string)
        with open(os.path.join(self.serialization_dir, RESULT_NAME), 'w') as f:
            print(report_string, file=f)
