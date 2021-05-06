# encoding: utf-8
from rshell.tools.params.models import project_parameters as __project_parameters
from os.path import dirname, realpath
from collections import UserDict

_params = __project_parameters()
root = dirname(realpath(__file__))


class GlobalParams(UserDict):
    def __getattr__(self, item):
        return getattr(_params, item)


class Default:
    def __init__(self):
        self.encoding = _params.encoding
        self.test_mode = _params.test_mode

    def __repr__(self):
        params_format = ', '.join(['{}={}'.format(key, getattr(self, key)) for key in self.__dict__])
        return f"{type(self).__name__}=({params_format})"

    def __str__(self):
        return "<{}> parameters -> ".format(type(self).__name__) + str([ele for ele in self.__dict__.keys()])


class Directories(UserDict):
    def __getattr__(self, item):
        return getattr(_params.directories, item)

    configuration = _params.directories.configuration
    parameters = _params.directories.parameters
    data = _params.directories.data
    suites = _params.directories.suites
    tools = _params.directories.tools


class Csvs(UserDict):
    def __getattr__(self, item):
        return getattr(_params.csv, item)

    separator = _params.csv.separator
    comment_character = _params.csv.comment_character


class Cooker(UserDict):
    def __getattr__(self, item):
        return getattr(_params.cooker, item)

    cluster_name_max_length = _params.cooker.cluster_name_max_length
    test_suite_name_max_length = _params.cooker.test_suite_name_max_length
    test_script_extension = _params.cooker.test_script_extension
    caller_separator = _params.cooker.caller_separator


class Parameters(UserDict):
    def __getattr__(self, item):
        return getattr(_params.parameters, item)

    conf_files = _params.parameters.conf_files


class Project(UserDict):
    def __getattr__(self, item):
        return getattr(_params.project, item)


default_params = Default()
directories_params = Directories()
project_params = Project()
csv_params = Csvs()
cooker_params = Cooker()
