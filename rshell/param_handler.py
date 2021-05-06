# -*- coding: utf-8 -*-
"""
Cette librairies permet la gestion des paramètres en général.

Ces principaux outils sont :

- la gestion des paramètres extraits des fichies de configuration
- la gestion des paramètres dans un fichier de paramètre du projet
- l'exécution de scripts en fonction de ces paramètres

Dans un soucis de mutualisation, cette librairie est très dépendantes d'autres éléments,
figurant pour la plupart dans tools

.. note::

    tools contient des outils plus back-end, leur utilisation peut être nécéssaire,
    pour cela param_handler fait l'intermédiaire, notamment pour récupérer les paramètres
    du projet.

"""
from csv import reader
from collections import namedtuple
import re
from os.path import split, exists, expandvars, join, abspath
import subprocess
from functools import partial
from datetime import datetime, timedelta
from time import sleep
from rshell.tools.params import project as _pp
from rshell.tools.params.models import file_parameters
from rshell.tools.exceptions import ShellExecutionError, NotConfiguredError, ConfigKeyError, ConfigContentError

dir_params = _pp.Directories()
csv_conf = _pp.Csvs()
CSV_SEPARATOR = csv_conf.SEPARATOR
CSV_COM_CARACTER = csv_conf.COMMENT_CHARACTER
CONF_DIR = dir_params.configuration
ENCODING = _pp.Default().ENCODING
CONF_FILES_PARAMETERS = _pp.Parameters().CONF_FILES
extension = ".cfg"
NO_EXECUTION_LOG = "ALERT : Le script n'a pas été exécuté!"
# le label est remonté à un niveau supérieur pour une meilleure gestion des données de conf
SimpleParam = namedtuple('parameter', 'id conf label')
"""
Cet élément permet de récupérer la clé, la liste des paramètres et le label quel
que soit la configuration exploitée.

Cette variable n'est utilisée que par les fonctions de ce module.
"""


def generate_file_tuples_dict():
    """
    Génère le dictionnaire type "objet" namedtuples des fichiers .cfg configurés.
    Permet la facilitation d'utilisation des données entrées.

    La configuration des tuples se fait sous forme de clé : [valeurs] dans
    le fichier de configuration indiqué dans config.ini

    L'exploitation et ne nommage de ces jeux de données est entièrement dynamique, pas
    besoin d'écrire dans robot ou le code le moindre nom ou la moindre donnée de ces fichier.
    Seul la clé est nécéssaire.

    .. note::

        Cette fonction est assez avancée, les autres fonctions du module l'exploitent
        suffisament pour ne pas avoir à utiliser celle-ci pour les cas simples.
        Ne réinventez pas la roue.


    :return: dictionnaire des namedtuples types des données dans les cfg
    """
    tuple_file_dict = dict()
    print(CONF_FILES_PARAMETERS)
    # aller chercher le fichier de param
    params = file_parameters(CONF_FILES_PARAMETERS)
    print(params)
    param_dict = params.files._asdict()
    # créer des tuples depuis le fichier de config.
    for key in params.files._asdict():
        result = namedtuple(key, [*param_dict.get(key)])
        tuple_file_dict[key + extension] = result
    return tuple_file_dict


# dicionnaire des namedtuples récupérant les données des fichiers .cfg : c'est la source de la représentation objet
# des configs.
file_dict = generate_file_tuples_dict()


def _contextual_config_tuple(conf_file_path):
    """
    Renvoie le namedtuple de la configuration correspondant au fichier.

    La forme du namedtuple est définie dans le fichier config.ini

    .. note ::

        En cas d'erreur du à l'exctraction des données, les autres méthodes renvoient
        aux fichiers de conf et param. Cette méthode ne vérifie que la présence du fichier
        de conf, pas son contenu.


    :param conf_file_path: path du fichier de conf
    :return:
    """
    try:
        return file_dict[split(conf_file_path)[-1]]
    except KeyError:
        raise NotConfiguredError("""
        Le fichier {} n'a pas de configuration prédéfinie.
        S'il s'agit d'un nouveau fichier de configuration, 
        vous pouvez ajouter son paramétrage dans {}.
        Auquel cas, le nom de fichier ou le chemin est incorrect.""".format(conf_file_path, __file__))


def _abspath_of_variables(list_of_values):
    result = []
    for ele in list_of_values:
        # si l'élément de conf commence par '$' (donc est potentiellement une variable d'env)
        if re.match(r'^\$', ele):
            # Ne plante pas si aucune expansion réalisée.
            result.append(expandvars(ele))
        elif re.findall(r'/', ele):
            # s'il s'agit d'un path relatif
            result.append(abspath(ele))
        else:
            result.append(ele)
    return result


def conf_file2params_tuples(conf_file_path):
    """
    Renvoie la liste complete des paramètres du fichier de conf sous le format
    namedtuple.

    Chaque jeu de donnée est humainement lisible, avec l'intitulé de chaque valeur.
    Pour consulter ces données, exécuter un "Log" dans rf du resultat de ce keyword.

    .. note ::

        L'exploitation des données ne se fait que par sélection d'un jeu avec sa clé.
        Une fonction existe déjà pour selectionner un jeu de données en foncion de la clé.
        Utilisez "Get Config", ne réinventez pas la roue.

    :param conf_file_path:
    :return:
    """
    assert isinstance(conf_file_path, str), "Le paramètre doit être de type string -> {}".format(type(conf_file_path))
    if not exists(conf_file_path):
        raise SyntaxError("le chemin {} pour le fichier de conf n'existe pas".format(conf_file_path))
    # récupération du namedtuple correspondant au fichier de conf
    conf_tuple = _contextual_config_tuple(conf_file_path)
    params_list = []
    with open(conf_file_path, 'r') as file:
        # csv-ification :)
        arrays = list(reader(file, delimiter=CSV_SEPARATOR))
    for param in arrays:
        # regex pour matcher tout string commençant par CSV_COM_CARACTER('#')
        reg = re.compile(r'^{}'.format(CSV_COM_CARACTER))
        # si la ligne n'est pas vide ET un commentaire
        if len(param) > 0 and not re.match(reg, param[0]) and not param[0].isspace():
            # extraction de l'id de la liste (1er élément)
            key = param.pop(0)
            # extraction du commentaire(dernier élément), le reste de param est la config ordonnée
            label = param.pop(-1)
            # expansion des variables en abspath (faites pour toutes les confs car les éléments après seront des tuples)
            conf = _abspath_of_variables(param)
            # le commentaire est remonté des paramètres car cela permet d'utiliser la conf d'un bloc
            try:
                params_list.append(SimpleParam(id=key, conf=conf_tuple(*conf), label=label))
            except TypeError:
                raise ConfigContentError("""
La conversion du CSV en namedtuple remonte un TypeError.
Cela peut provenir d'une donnée manquante ou en trop dans le fichier.
Veuilez vérifier:
- le nombre d'éléments par ligne dans le fichier {}
- en particulier si le label est entré ou à défaut un "{}" est placé au bout du jeu de données
- si un "{}" est contenu dans les données d'au moins une ligne.""".format(conf_file_path, CSV_SEPARATOR, CSV_SEPARATOR))
    return params_list


def get_config(config_key, conf_file_name):
    """
    Renvoie la configuration correspondant au fichier de conf "conf_file_name"
    et à la clé "config_key" de la configuration (le premier champs de la ligne).

    .. note ::

        Les cas d'erreurs sont le plus souvent une clé erronnée, si le
    """
    file_content = conf_file2params_tuples(join(CONF_DIR, conf_file_name.lower()))

    # récupération de la conf correspondante, ou fail provoqué si pas de correspondances
    for conf in file_content:
        if conf.id == config_key:
            print(conf.label)
            return conf
    else:
        raise ConfigKeyError("""
        La clé {} n'est pas reconnue dans le fichier {}.
        Vérifiez :
        - la syntaxe de la clé
        - le fichier de configuration visé""".format(config_key, conf_file_name))


# version limité de file_parameters, avec 'Run_Script.cfg' en 2e paramètre
get_script_conf = partial(get_config, conf_file_name='run_script.cfg')


def execute_file_with_params(file2execute, config_key, config_file_path):
    """
    Excécute un fichier shell avec paramètres.
    Les paramètres sont récupéré par le config_key dans le fichier de conf config_file_path.

    Version root de l'utilisation d'un fichier de paramétrage, comporte des obligations :

        - les paramètres doivent avoir comme structure :
            clé;<liste d'arguments ordonnés de gauche à droite>; commentaire(label)

        - le fichier de paramètre doit être réfécencé dans Params/ini_files/conf_files.ini:
            sous forme <clé:nom de fichier> : [<valeurs:liste des noms d'arguments>]

            Le label et la clé ne sont pas indiqués dans les paramètres.

    .. note ::

        Pour l'exécution d'un fichier réccurente, le keyword ``Run Script`` permet une utilisation simplifiée.
        Les paramètres peuvent alors être récupérés par ``Get Config`` dans un autre fichier de configuration.


    :param file2execute: path du fichier à exécuter
    :param config_key: clé dans le fichier de configuration
    :param config_file_path: path du fichier de configuration

    """
    config = get_config(config_key, config_file_path)
    # arguments à transmettre, sous format string (en list ne concidère pas les paramètres en tant que tel)
    command_args = " ".join([file2execute, *config.conf])
    # récupération du path root de l'exécution
    local = config.conf.directory
    status_log = """
    Arguments :
        fichier exécuté                :     {}
        fichier de configuration       :     {}
        clé dans le fichier            :     {}
        -------------------------------
    Parametres :
        paramètres récupérés de la clé :     {}
        parametres fournis             :     {}
        path d'exécution               :     {}
        -------------------------------
    Commandes :
        commande exécutée              :     {}
        code retour                    :     {}
        stdout                         :     {}
        stderr                         :     {}
        """
    # exécution de la commande avec les arguments, pipe des sorties, donc pas d'exception à l'exécution
    process = subprocess.run(command_args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
    # le log complet
    print(status_log.format(file2execute, config_file_path, config_key, config, [*config.conf],
                            local, command_args, process.returncode,
                            process.stdout.strip().decode("ASCII"), process.stderr.strip().decode("ASCII")))
    # provoque un fail si rc != 0, les logs seront sortis au dessus
    if process.returncode != 0:
        raise ShellExecutionError("L'exécution du script remonte une erreur : {}".format(process.returncode))


def run_script(file_key, *parameters, expected_rc='0'):
    """
    Fonction generale pour l'execution d'un script avec la configuration de run_script.cfg pour le fichier.
    Les paramètres de l'exécution sont à noter à la suite de la clé.

    Le returncode requis est par défaut "0" mais peut être modifié en indiquant une valeur à expected_rc.

    .. warning::

        Tous les paramètres doivent être sous le format string. Si un paramètre est renvoyé sous format
        numérique par exemple, l'exécution entrera en exception.
        Sous robotframework, une valeur ecrite est par défaut un string.


    :param expected_rc: défaut 0. code retour d'exécution souhaité
    :param file_key: clé des paramètres dans run_script.cfg
    :param parameters: paramètres éventuels indiqués à la suite de la commande notée dans run_script.cfg

    """
    conf = get_script_conf(file_key).conf
    command_args = " ".join([conf.script, *parameters])
    status_log = """    
---------- Arguments -----------
                           clé :     {}
---------- Parametres ----------
            parametres fournis :     {}
                           cwd :     {}
---------- Commandes -----------
             commande exécutée :     {}
                   code retour :     {}
-------------------------------
|           stdout            |                  
-------------------------------
{}
---------- end stdout ---------
-------------------------------
|           stderr            |  
-------------------------------
{}
---------- end stderr ---------
"""
    try:
        # pipe des sorties, aucun rc ne renvoie d'exception, seul cas est le cwd
        process = subprocess.run(command_args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 cwd=conf.directory)
    # exception sur le cwd, c'est le seul élément qui peut provoquer une exception sur l'execution de process
    except NotADirectoryError:
        print(NO_EXECUTION_LOG)
        raise NotADirectoryError("Le chemin {} n'existe pas ou n'est pas un path.".format(conf.directory))
    print(status_log.format(conf.script, [*parameters],
                            conf.directory, command_args, process.returncode,
                            process.stdout.strip().decode(ENCODING), process.stderr.strip().decode(ENCODING)))

    if process.returncode != int(expected_rc):
        raise ShellExecutionError("L'exécution du script remonte une erreur\nstdout   : {}\nExpected : {}"
                                  .format(process.returncode, expected_rc))
    return process.stdout


def run_script_as_daemon(file_key, *parameters):
    """
    Version de Run Script ou le processus s'execute en tache de fond, le keyword lance le processus, et se termine sans
    attendre le retour de l'exécution.

    .. note::

        Les sorties standards stdout, stderr et rc sont pipées et ne peuvent être récupérées.


    :param file_key: clé des paramètres dans run_script.cfg
    :param parameters: paramètres éventuels indiqués à la suite de la commande notée dans run_script.cfg

    """
    status_log = """    
    ---------- Arguments -----------
                               clé :     {}
    ---------- Parametres ----------
                parametres fournis :     {}
                               cwd :     {}
    ---------- Commandes -----------
                 commande exécutée :     {}
    """
    conf = get_script_conf(file_key).conf
    command_args = " ".join([conf.script, *parameters])
    # Popen passe la commande en daemon. PIPE sinon il affiche les logs en console
    subprocess.Popen([conf.script, *parameters], cwd=conf.directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(status_log.format(conf.script, [*parameters],
                            conf.directory, command_args))


def check_flow(id):
    """
    Verifie le contenu du flow et renvoie une réponse selon les paramètres:
        - Exception si le contenu est différent de data.conf.isFileExpected
        - pass et log si le contenu est conforme à data.conf.isFileExpected

    data.conf.isFileExpected est un paramètre du fichier check_flow.cfg, numérique tansformé en booléen,
    il statue sur le besoin d'un contenu (1 pour True) ou pas (0 pour False)

    :param id: clé de la configuration dans check_flow.ini
    """
    data = get_config(id, 'Check_Flow.cfg')
    stdout = run_script("check_flow", data.conf.applicationCode, data.conf.flowStatus, "FIL_IDT")

    assert isinstance(int(data.conf.isFileExpected), int) and (
            int(data.conf.isFileExpected) == 1 or int(data.conf.isFileExpected) == 0), \
        "data.conf.isFileExpected doit le chiffre 0 ou 1 : %s" % data.conf.isFileExpected
    regex = re.compile(r'no rows selected')
    phrase = str(stdout.decode(ENCODING))
    contains = False if re.findall(regex, phrase) else True
    result = True if int(data.conf.isFileExpected) == contains else False
    log = """
        Contenu dans le flow : {}
        Expected             : {}
        """.format(contains, True if data.conf.isFileExpected == "1" else False)
    print(log)
    if not result:
        raise ShellExecutionError("Check flow -> KO")
    else:
        print("Check flow -> OK")


def check_flow_until_it_match(id, max_time=60):
    """
    Lance la fonction check flow jusqu'à ce qu'elle rende une réponse non fail, dans
    la limite du délai donnée (défaut 1h)

    .. note::

        Ce keyword est dépendant de la configuration du fichier check_flow.cfg dans
        conf_files.ini


    :param id: clé de la configuration dans check_flow.ini
    :param max_time: temps max de vérification en minutes, par défaut 60.

    """
    start = datetime.now()
    while True:
        try:
            check_flow(id)
            break
        except ShellExecutionError:
            sleep(5)
            if datetime.now() > (start + timedelta(minutes=max_time)):
                raise TimeoutError("Le délai de %dh est dépassé" % max_time)


def declare_flow(id):
    """
    Déclare les fichiers dans le flow en utilisant le script declarerNFichiersFLOW.sh.

    .. note::

        Ce keyword est dépendant de la configuration du fichier check_flow.cfg dans
        conf_files.ini

    :param id: clé de la configuration dans check_flow.ini

    """
    data = get_config(id, "Declare_Flow.cfg")
    run_script("declare_flow", data.conf.applicationCode, data.conf.flowAgent, data.conf.directory,
               data.conf.filePattern)


def clean_flow(id):
    """
    Supprime tous les fichier dans le flow en exécutant le script purgeFLOW.sh.

    .. note::

        Ce keyword est dépendant de la configuration du fichier check_flow.cfg dans
        conf_files.ini

    :param id: clé de la configuration dans check_flow.ini

    """
    data = get_config(id, "Clean_Flow.cfg")
    run_script("purge_flow", data.conf.applicationCode)


def directory_parameters():
    """
    Renvoie une instance de la classe DirectoriesParams, dont les attributs sont les pathes des dossiers du projet

    .. note::

        La classe DirectoriesParams se situe dans Librarie.tools.params.project_params.
        Cette classe est dépendante des paramètres de config.ini


    :return: namedtuple
    """
    return _pp.Directories()


def cluster_parameters():
    """
    Renvoie une instance de la classe ParametersParams, dont les attributs sont les pathes des fichiers de
    paramétrage des scripts robot des clusters.

    .. note::

        La classe ParametersParams se situe dans Librarie.tools.params.project_params.
        Cette classe est dépendante des paramètres de config.ini


    :return: namedtuple
    """
    return _pp.Parameters()


def default_parameters():
    """
    Renvoie une instance de la classe DefaultParams, dont les attributs
    sont les paramètres indiqués dans la rubrique DEFAULT du fichier config.ini.

    .. note::

        La classe DefaultParams se situe dans Librarie.tools.params.project_params.
        Cette classe est dépendante des paramètres de config.ini


    :return: namedtuple
    """
    return _pp.Default()


def project_parameters():
    """
    Renvoie une instance de la classe ProjectParams, dont les attributs sont les paramètres propres au
    projet inscrits dans la rubrique PROJET du fichier config.ini

    .. note::

        La classe ProjectParams se situe dans Librarie.tools.params.project_params.
        Cette classe est dépendante des paramètres de config.ini


    :return: namedtuple
    """
    return _pp.Project()


def redis_parameters():
    """
    Renvoie une instance de la classe RedisParams dont les attributs sont les paramètres
    d'exploitation du SGBD Redis pour le projet.

    .. note::

        La classe RedisParams se situe dans Librarie.tools.params.project_params.
        Cette classe est dépendante des paramètres de config.ini


    :return: namedtuple
    """
    return _pp.RedisParams()
