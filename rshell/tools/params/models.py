# encoding: utf-8
"""
Fichier gérant la lecture des paramètres.
Il exploite des fichiers de type param au format :
[titre]
cle : valeur

IL peut parser les valeurs de type dictionnaire et liste, ex:
cle1 : [val1, val2, val3]
cle2 : {scle1: val1, scle2: [sval1, sval2, sval3]}

le fichier "config.ini", à la racine du projet, contient toutes les références du projet, les données de ce fichier
détermine tous les pathes du projet.
la fonction project_parameters renvoie un namedtuple dynamiquement créé des paramètres de config.ini
Il n'y a donc pas d'autocomplétion pour son utilisation. Pour compenser à ces éléments récurrents, un script
project_param.py contient des classes explicitant les valeurs. Il est à faire évoluer en même temps que le fichier
config.ini
"""
import configparser
from collections import abc
from keyword import iskeyword
from re import compile, findall, split as re_split
from rshell.tools.exceptions import IniFileError
from os.path import expandvars, realpath
from rshell.tools.params import CONFIG_ENCODING, CONFIG_FILE_NAME
from numbers import Number

PROJECT_CONFIG_FILE = realpath(CONFIG_FILE_NAME)


def _evaluated_value(value):
    if value == '' or not value:
        return ''
    if not isinstance(value, str):
        return value
    isList = compile(r"^\[.+\]$")
    # dirty list case
    if findall(isList, value):
        result = re_split(r', ?', value.strip(']['))
        return [expandvars(ele) for ele in result]
    try:
        # all cases of bool, int or others.
        if isinstance(eval(value), bool) or isinstance(eval(value), Number):
            return eval(value)
    except (NameError, SyntaxError):
        pass
    return expandvars(value)


class FrozenParams:
    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            if iskeyword(key):
                key += '_'
            if not key.isidentifier():
                key = 'v_' + key
            self.__data[key] = value

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            return FrozenParams(_evaluated_value(self.__data[name]))

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

    def __repr__(self):
        return str(self.__data)

    def __str__(self):
        return self.__repr__()


def file_parameters(file):
    """
    Renvoie la liste des paramètres du fichier, sous le format FrozenParams
    :param file:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(file, encoding=CONFIG_ENCODING)

    try:
        param_dict = config._sections
        param_dict.update(dict(config['DEFAULT']))
        return FrozenParams(param_dict)
    except ValueError as ve:
        raise IniFileError("""Le fichier de paramétrage contient une clé non conforme au format demandé.
        Une clé doit contenir des caractères a-zA-Z, des underscore, et des chiffres sauf pour le premier caractère.""")


def project_parameters():
    """
   Renvoie un FrozenParams contenant l'ensemble des paramètres introduits dans CONFIG_FILE_NAME(config.ini par défaut).
   :return:
   """
    return file_parameters(PROJECT_CONFIG_FILE)
