# -*- coding: utf-8 -*-
"""
Bibliothèque Local Directory Indexer.

Permet de récuperer les chemin de fichiers dans le projet avec une chaine
de clés implicites appelée "caller".
le caller est une suite de deux mots qui représentent le fichier visé.
Il est composé:
    - du nickname, il s'agit de l'élément visé:
        - TEST pour le test, il renvoie vers les fichiers de données du test
    - du nom du fichier recherché, ce peut être:
        - ATTENDU, pour le fichier .att du test
        - RESULTAT pour le fichier .res du test
        - ENTRANT pour le fichier .dat du test
        - le nom du fichier simplement.

Le nickname "TEST" renvoie au testsuite en cours, cela permet de récupérer les
fichiers de données liés à ce test.
On peut chercher les fichiers par un mot clé "ATTENDU", "RESULTAT" et "ENTRANT".
Si le fichier est plus spécifique, on peut noter son nom directement.

exemples:
    "get local file  TEST->ENTRANT" renvoie "/Data/cluster/testencours/nomtest.dat"
    "set local file TEST->ATTENDU" renvoie "/Data/cluster/testencours/nomtest.att"
    "get local file TEST->unfichier.ext" renvoie "/Data/cluster/testencours/unfichier.ext"

"""
from os import path, mkdir
from rshell.rf_dependant.rf_variables import _get_test_suite_name, _get_suite_source
from rshell.tools.params.project import Directories

dir_params = Directories()

DOT = "."

ATTENDU = "ATTENDU"
RESULTAT = "RESULTAT"
ENTRANT = "ENTRANT"

TESTSUITE_DIR_NAME = "Test_Suite"
DATA_DIR_NAME = "Data"
TOOLS_DIR_NAME = "Tools"

ROBOT_EXTENSION = "robot"
ATTENDU_EXTENSION = "att"
RESULTAT_EXTENSION = "res"
ENTRANT_EXTENSION = "dat"

TEST = "TEST"
CLUSTER = "CLUSTER"
DATA = "DATA"
TOOLS = "TOOLS"
TESTSUITES = "TESTSUITES"
CALLER_SEPARATOR = "->"
NICKNAMES = (TEST,
             CLUSTER,
             DATA,
             TOOLS,
             )

DATA_REPERTORY = dir_params.data
TESTSUITES_REPERTORY = dir_params.suites
TOOLS_REPERTORY = dir_params.tools


def set_local_file(caller):
    """
    Génère un nom de fichier et son chemin.
    Vérifie que chaque dossier du chemin existe ou à défaut le crée.
    Ne fonctionne qu'avec le nickname "TEST"
    :param caller:
    :return: file path
    """
    dir_pathes = _set_dir_pathes_related_to_the_caller(caller)
    (nickname, *directories, filename) = _get_splitted_caller(caller)
    switcher = {ATTENDU: _get_test_suite_name() + DOT + ATTENDU_EXTENSION,
                RESULTAT: _get_test_suite_name() + DOT + RESULTAT_EXTENSION,
                ENTRANT: _get_test_suite_name() + DOT + ENTRANT_EXTENSION
                }
    implicit_file_name = switcher.get(filename)
    # utilise uniquement le path commençant par Data
    if implicit_file_name:
        return path.join(dir_pathes[1], implicit_file_name)
    else:
        return path.join(dir_pathes[1], filename)
    # TODO fonctionnement avec les nicknames TOOLS et testsuite


def get_local_file(caller):
    file_path = set_local_file(caller)
    if path.exists(file_path):
        return file_path
    else:
        raise ValueError("Le fichier {} n'existe pas.".format(file_path))


def _get_dir_pathes_related_to_the_caller(caller):
    (nickname, directories, filename) = _get_splitted_caller(caller)
    if nickname in NICKNAMES:
        switcher = {TEST: _get_test_nickname_pathes(),
                    CLUSTER: _get_cluster_nickname_path(),
                    DATA: _get_data_nickname_path(),
                    TOOLS: _get_tools_nickname_path(),
                    }
        nickname_path = switcher[nickname]()
        if directories:
            dir_path = (path.abspath(single_path + "/" + "/".join(directories)) for single_path in nickname_path)
            return dir_path
        return nickname_path
    else:
        raise ValueError("Le nickname \"{}\" n'existe pas".format(nickname))


def _set_dir_pathes_related_to_the_caller(caller):
    (nickname, directories, filename) = _get_splitted_caller(caller)
    if nickname in NICKNAMES:
        switcher = {TEST: _get_test_nickname_pathes,
                    CLUSTER: _get_cluster_nickname_path,
                    DATA: _get_data_nickname_path,
                    TOOLS: _get_tools_nickname_path,
                    }
        nickname_pathes = switcher[nickname.upper()]()
        if directories:
            dir_path = []
            for item in nickname_pathes:
                mkdir(item) if not path.exists(item) else None
                new_item = item
                for directory in directories:
                    new_item += "/" + directory
                    None if path.exists(new_item) else mkdir(new_item)
                dir_path += [new_item]
            return dir_path
        return nickname_pathes
    else:
        raise ValueError("Le nickname \"{}\" n'existe pas".format(nickname))


def _get_splitted_caller(caller):
    assert isinstance(caller, str), "La méthode n'accepte qu'un paramètre au format string."
    (nickname, *directories, filename) = caller.split(CALLER_SEPARATOR)
    return nickname, directories, filename


def _get_test_nickname_pathes():
    """
    Retourne les chemins du testsuite courant :
        - le dossier contenant le testsuite
        - un dossier dans Data/ avec l'architecture du chemin du testsuite
        - un dossier dans Tools/ avec l'architecture du chemin du testsuite


    :return: (test_dir, data_dir, tools_dir)
    """
    # récupération du chemin du test suite
    splitted_suite_source = path.split(_get_suite_source())
    # recuperation du chemin du directory
    suite_dir = splitted_suite_source[0]
    # recuperation du nom du test sans son extension
    suite_name = splitted_suite_source[1].split(DOT)[0]
    if path.exists(suite_dir):
        test_dir = suite_dir
        # remplacement brut de test_suite par Data
        data_dir = path.join(suite_dir.replace(TESTSUITE_DIR_NAME, DATA_DIR_NAME), suite_name)
        tools_dir = path.join(suite_dir.replace(TESTSUITE_DIR_NAME, TOOLS_DIR_NAME), suite_name)
        return test_dir, data_dir
    else:
        raise ValueError("Problème avec le fichier de test courant;\n"
                         "chemin obtenu : {}".format(suite_dir))


def _get_cluster_nickname_path():
    suite_name = _get_suite_source()
    return path.split(suite_name)[:-1]


def _get_data_nickname_path():
    return DATA_REPERTORY


def _get_tools_nickname_path():
    return TOOLS_REPERTORY


def _get_testsuites_nickname_path():
    return TESTSUITES_REPERTORY
