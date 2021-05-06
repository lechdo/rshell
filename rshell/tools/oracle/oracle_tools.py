# encoding:utf-8
"""

"""
import cx_Oracle
from rshell.fileTools import file_config as _file_config
from rshell.tools.params.project import Project
from rshell.tools.oracle.contract import SELECT_TABLE_COLUMNS_BY_TABLE_NAME_AND_OWNER

# really specific environment file.
ora_conf = Project().config_oracle_file
oracle_config = _file_config(ora_conf)


def _oracle_action(*args, condition):
    """
    Fonction generique permettant de se connecter a Oracle sur Platon en utilisant les parametres
    dans ora_conf.

    ATTENTION les attributs de confs sont notés en specifique, si vous changez les parametres, assurez vous de
    changer les attributs de conf si necessaire.

    :param args:
    :param condition:
    :return:
    """
    # log en premier car sinon on n'a pas ces infos dans rf
    print('Oracle connection -> user:{} - pwd:{} - {}:{}/{}'.format(oracle_config.P_USRTRT, oracle_config.P_PWDTRT, oracle_config.P_HOSTTRT,
                                                                    oracle_config.P_PORTTRT, oracle_config.P_SIDTRT))
    # les attributs dynamiques sont notés en brut, l'ide n'aime pas ça, mais creer un intermediaire
    # prendrait des heures et obligerai à ajouter un fichier de parametres, je concidere donc la methode en specifique
    connection = cx_Oracle.Connection(oracle_config.P_USRTRT, oracle_config.P_PWDTRT,
                                      "{}:{}/{}".format(oracle_config.P_HOSTTRT, oracle_config.P_PORTTRT, oracle_config.P_SIDTRT))
    print('Oracle connection -> CONNECTED')
    # generation du cursor
    cursor = connection.cursor()
    # utilisation conditionnelle du cursor, cette methode 1e classe est necessaire a l'utilistaion de cette fonction
    result = condition(cursor, *args)
    connection.commit()
    print('Oracle connection -> COMMITED')
    connection.close()
    print("Oracle connection -> CLOSED")
    # Le retour est generique, si pas besoin de retour, renvoie None
    return result


def table_columns(table_name):
    """
    Supprime le contenu de chaque table de la liste.
    Effecute requete par requete.

    L'integration du nom de table dans la requete fait qu'une exception sera critique et provoquera l'arret
    du process (pour les parametres, l'excepetion n'est pas critique)
    :param tables:
    :return:
    """

    def select(cursor, table_name):
        print("<Getting table columns list> -> {}".format(table_name))
        result = cursor.execute(SELECT_TABLE_COLUMNS_BY_TABLE_NAME_AND_OWNER,
                       table_name=table_name, owner=oracle_config.conf.P_USRTRT)
        print(result)

    # execution de l'action en utilisant la fonction scope
    result = _oracle_action(table_name, condition=select)
    return result
