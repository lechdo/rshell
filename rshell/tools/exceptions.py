# encoding: utf8
class NotComparableError(Exception):
    pass


class CompareError(Exception):
    pass


class IniFileError(Exception):
    pass


class ConfigFileError(Exception):
    pass


class ConfigKeyError(Exception):
    pass


class ConfigContentError(Exception):
    pass


class CsvContentError(Exception):
    pass


class ShellExecutionError(Exception):
    pass


class NotConfiguredError(Exception):
    pass


class RedisError(Exception):
    pass
