# -*- coding: utf-8 -*-
"""
Contient differentes fonctions utiles
"""
import json
from os import path, walk, remove
import re
from collections import namedtuple


def etendre_variables(path_file):
    """
    Replace in a path the environment variable by his complete equivalent
    Example :
    environment variable :
    $HOME=/vat/opt

    etendre_variables($HOME/foo/bar) >> /vat/opt/foo/bar

    :param:
        path_file: the path to extend
    :return:
        path_file_complete: complete path
    """
    return path.expandvars(path_file)


def replace_column_by_null(content_file, liste_index_column=None):
    """
    Replace content of column by null

    :param:
        content_file: content of a file
        liste_index_column: list of index column to convert to null
    :return:
        content_file_changed: content of a file where some column contains null values
    """
    row_file = content_file.split("\n")

    if liste_index_column is None:
        liste_index_column = []

    row_file_changed = []

    for row in row_file:
        if row != "":
            column = row.split(";")
            for index_column in liste_index_column:
                column[int(index_column)] = ''
            row = ";".join(column)
        row_file_changed.append(row)

    content_file_changed = "\n".join(row_file_changed)

    return content_file_changed


def sort_json_file(path_file, path_file_output):
    """
    Format and sort json file

    :param:
        path_file: the path to file to format and sort
        path_file_output: the path to file to format and sort
    :return:
        code_result:
            0 pour le traitement s'est mal déroulé
            1 pour le traitement s'est bien déroulé
    """

    code_result = 0
    if not path.isfile(path_file):
        return code_result

    file_reader = open(path_file)
    data_file = json.load(file_reader)
    file_reader.close()

    file_writer = open(path_file_output, 'w')
    json.dump(data_file, file_writer, indent=4, sort_keys=True)
    file_writer.close()

    return 1


def clear_old_data(folder_path):
    """
    Supprime tous les fichiers présents dans le dossier.
    Execution en daemon.
    :param folder_path:
    :return:
    """
    if path.exists(folder_path):
        files = []
        for (_, __, filenames) in walk(folder_path):
            files.extend(filenames)
        print("Fichiers répertoriés : {}".format(files))
        for file in files:
            print("Suppression -> %s" % file)
            remove(path.join(folder_path, file))
    else:
        print("Le chemin %s n'existe pas" % folder_path)


def suppress_file(path):
    """
    Supprime le fichier du path s'il existe.
    Fail si le chemin est un chemin de dossier.
    :param path:
    :return:
    """
    if path.exists(path):
        if path.isfile(path):
            print("Delete file -> %s" % path.split(path)[-1])
            remove(path)
            print("Delete file -> DONE")
        else:
            raise IsADirectoryError("Le path %s est un dossier" % path)
    else:
        print("Le path ne renvoie à aucun fichier -> %s" % path)


def list_dir_files(dir_path, search_pattern=None):
    """
    retourne une liste des fichiers contenus dans le dossier correspondant
    au pattern.
    Si le pattern n'est pas indiqué, retourne l'ensemble des fichiers du dossier.
    :param search_pattern:
    :param dir_path:
    :return:
    """
    assert path.exists(etendre_variables(dir_path)), "Le path %s n'existe pas." % dir_path
    files = [ele for ele in walk(etendre_variables(dir_path))][0][2]
    print("files in {} -> {}".format(dir_path, files))
    if search_pattern:
        print("Pattern search -> '%s'" % search_pattern)
        search_list = []
        regex = re.compile(search_pattern)
        for file in files:
            search_list.append(file) if re.findall(regex, str(file)) else None
        print("Finded -> {}".format(search_list if search_list else None))
        return search_list
    else:
        return files


def file_config(file):
    """
    Recuperation des paires cle=valeur dans le fichier.
    Les cles ne peuvent commencer par un chiffre, aussi toute cle est precedee par "P_" pour
    palier a cette difficulte.

    La variable renvoyee possede un attribut pour chaque cle dans le fichier.

    Fonction cree pour recuperer les credentials dans $FICPRMORA dynamiquement
    sans passer par une serie de kw robotframework.

    :param file:
    :return: namedtuple
    """
    # etendre la variable au cas où
    file_path = path.expandvars(file)
    assert path.exists(file_path), "Le fichier {} n'existe pas, veuillez verifier le parametre".format(file)
    with open(file_path, 'r', encoding='ISO-8859-1') as file2read:
        data = file2read.read()
    # recuperation du nom
    params = {}
    regex = re.compile(r'(.+)=(.+)')
    # recuperation des elements cle=valeur dans le fichier
    vals = re.findall(regex, data)
    # assignation en dict, P_ car certaines cles commencent par un nombre
    for key, value in vals:
        params["P_" + key] = value
    # creation dynamique d'un namedtuple avec les cles. namedtuple car syntaxe + simple, meilleurs perfs, logs + clair
    file_params = namedtuple('params', [*params.keys()])
    # assignation des valeurs.
    result = file_params(*params.values())
    print("Utilisation des valeurs de {}.\nATTENTION, chaque cle est precedee par 'P_' dans son attribut!".format(file))
    return result


def file_archive(file_name, dir_path):
    """
    Renvoie le contenu du fichier dans le stdout.
    Utile pour le transfert des logs dans le fichier de sortie rf.
    :param file_name:
    :return:
    """
    with open(path.join(etendre_variables(dir_path), file_name), 'r', encoding="ISO-8859-1") as file:
        archive = [ele.strip() for ele in file.readlines()]
    print("-" * 50)
    print(" " * 15 + "<<<{}>>>".format(file_name))
    print("-"*50 + "\n")
    [print(ele) for ele in archive]
