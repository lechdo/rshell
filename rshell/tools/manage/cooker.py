# encoding: utf-8
"""
Ce script est un outils de facilitation.
Il permet de créer les tests et leur arborescerence selon une norme prédéfinie.

.. code-block::

    TestSuite
        /Cluster
            /Testsuite.robot

Le dossier cluster est généré en title, le testsuite aussi.
Une arborescence de dossiers peut être générée dans DATA_DIR_NAME et TOOLS_DIR_NAME.

Un cluster doit être créé avant la création de son contenu.

.. danger::

    **Toute modification de nom (dossier ou test) entrainera une différenciation avec les dossier et fichier
    automatiquement générés.**

    Lors d'une telle modification, l'option 3 (mise à jour) est susceptible de recréer une arborescence supplémentaire.
    l'arborescence initiale, bien qu'existante, ne sera plus reconnue par le projet !!

    Cette opération est à eviter (norme d'écriture des noms, perte des chemins...), mais peut permettre de renommer
    un test ou un cluster. Dans ce cas :
        - renommer le test ou le cluster
        - avec cooker, mettez à jour l'arborescence.
        - dans DATA_DIR_NAME et TOOLS_DIR_NAME, migrer le contenu de l'ancienne arborescence dans la nouvelle
        - supprimer l'ancienne arborescence
        - avec cooker remettez à jour
        - si aucune arborescence ne se crée de nouveau, la migration a réussi

"""
from os import path, walk, mkdir
from glob import glob
from rshell.tools.params.project import Directories, Cooker
from rshell.tools.params.models import project_parameters

self_params = Cooker()
########################################################################################################################
# PARAMETRES
########################################################################################################################
# pathes
DIRECTORIES_PARAMS = Directories()
TEST_SUITE_DIR_PATH = DIRECTORIES_PARAMS.suites

# noms de dossiers du projet
global_config = project_parameters()
TESTSUITE_DIR_NAME = global_config.directories.tests_suites
DATA_DIR_NAME = global_config.directories.data
TOOLS_DIR_NAME = global_config.directories.tools

# Configuration
###############

# Séparateur d'appel dans les commandes
CALLER_SEPARATOR = self_params.CALLER_SEPARATOR
TEST_MAX_LENGTH = self_params.TEST_SUITE_NAME_MAX_LENGTH
CLUSTER_MAX_LENGTH = self_params.CLUSTER_NAME_MAX_LENGTH

# Elements inhérents au code
############################

DOT = "."
ROBOT_EXTENSION = self_params.TEST_SCRIPT_EXTENSION
WRITE = "w"


########################################################################################################################
# CODE
########################################################################################################################
def _update_dir_architecture(cluster=None, testsuitename=None):
    """
    mets à jour l'architecture des dossiers dans le projets.
    Crée un dossier par cluster, un dossier par testsuite, selon la même
    organisation que le dossier Test_Suite, dans les répertoires Data et Tools.
    :param cluster:
    :return:
    """
    print("mise a jour de l'arborescence des tests")
    testsuite_walker = list(walk(TEST_SUITE_DIR_PATH))
    testsuite_dirs = [element[0] for element in testsuite_walker][1:]
    for directory in testsuite_dirs:
        data_dir = directory.replace(TESTSUITE_DIR_NAME, DATA_DIR_NAME)
        tools_dir = directory.replace(TESTSUITE_DIR_NAME, TOOLS_DIR_NAME)
        None if path.exists(data_dir) else mkdir(data_dir)
        None if path.exists(tools_dir) else mkdir(tools_dir)
        current_dir = path.split(directory)[1]
        testfiles = glob(path.join(directory, "*" + DOT + ROBOT_EXTENSION))
        if cluster:
            print("Cluster {}".format(current_dir)) if current_dir == cluster else None
        else:
            print("Cluster {}".format(current_dir))
        for testfile in testfiles:
            testname = path.split(testfile)[1].split(DOT).pop(0)
            data_testfile_dir = path.join(data_dir, testname)
            tools_testfile_dir = path.join(tools_dir, testname)
            None if path.exists(data_testfile_dir) else mkdir(data_testfile_dir)
            None if path.exists(tools_testfile_dir) else mkdir(tools_testfile_dir)
            if testsuitename:
                print("    -> testsuite {testname}".format(**locals())) if testname == testsuitename else None
            else:
                print("   -> testsuite {testname}".format(**locals()))

    print("Fin de mise a jour.")


def _create_new_cluster():
    cluster = input("Nom du cluster:").title()
    try:
        assert len(cluster) < self_params.CLUSTER_NAME_MAX_LENGTH and cluster.replace("_", "a").replace(".",
                                                                                                        "a").isalnum()
    except AssertionError:
        print("Mauvais format de cluster (- de 20 caracteres, pas de carateres spéciaux).")
        return

    cluster_path = path.join(TEST_SUITE_DIR_PATH, cluster)
    if path.exists(cluster_path):
        print("Le cluster existe deja.")
    else:
        mkdir(cluster_path)
        print("Cluster cree.")
        _update_dir_architecture(cluster)


def _create_new_test_suite():
    service = input("Entrez cluster{}testsuitename :".format(self_params.CALLER_SEPARATOR))
    (cluster, testsuite) = [element.title() for element in service.split(self_params.CALLER_SEPARATOR)]
    try:
        assert len(cluster) < CLUSTER_MAX_LENGTH and cluster.replace("_", "a").replace(".", "a").isalnum()
        assert len(testsuite) < TEST_MAX_LENGTH and testsuite.replace("_", "a").replace(".", "a").isalnum()
    except AssertionError:
        print("Mauvais format (- de 20 caracteres, pas de carateres spéciaux).")
        return

    cluster_path = path.join(TEST_SUITE_DIR_PATH, cluster)
    testsuite_path = path.join(TEST_SUITE_DIR_PATH, cluster, testsuite + DOT + ROBOT_EXTENSION)
    if not path.exists(cluster_path):
        print("Le cluster n'existe pas, veuillez le creer.")
    elif path.exists(testsuite_path):
        print("le testsuite existe deja.")
    else:
        with open(path.join(TEST_SUITE_DIR_PATH, cluster, testsuite + DOT + ROBOT_EXTENSION),
                  WRITE) as test_file:
            test_file.write("*** Settings ***\n\n\n")
            test_file.write("*** Variables ***\n\n\n")
            test_file.write("*** Test Cases ***\n")
        print("testsuite cree.")
        _update_dir_architecture(cluster, testsuite)


def _make_choice(choice):
    switcher = {1: _create_new_cluster,
                2: _create_new_test_suite,
                3: _update_dir_architecture,
                }
    try:
        switcher[choice]()
    except KeyError:
        print("Valeur au dela des choix.")


def main():
    presentation = """
    Quelle action souhaitez-vous realiser?
    1 - Creer un nouveau Cluster
    2 - Creer un nouveau test
    3 - mettre a jour l'arborescence des tests (cree dossiers dans data et tools)
    """

    print(presentation)
    response = input("Operation? :")
    try:
        _make_choice(int(response))
    except ValueError:
        print("Reponse incorrecte.")

    print("Fin d'operation.")


if __name__ == '__main__':
    main()
