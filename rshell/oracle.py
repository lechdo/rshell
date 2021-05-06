# -*- coding: utf-8 -*-
"""
Librairie pont entre cx_oracle et robotframework.
cx_oracle est conçu pour le code, l'execution de ses methodes s'avere complique dans les scripts *.robot

Ce script comprend:

    - une fonction pour recuperer les elements credentials dans un fichier de maniere dynamique
      et simplifiee (il faut tout de meme connaitre les cles pour les valeurs)
    - une fonction generique de haut niveau (prenant d'autres fct en parametre) permettant la connexion, l'execution
      d'une operation puis la deconnexion sur la base Oracle
    - des fonctions 1e classe (standards) et scope, destinees autiliser la fonction generique, pour specifier
      une operation.

La structure de chaque reponse specifique repond a un schema simple et explicite. Si un autre besoin apparait,
il suffit de reprduire le pattern en changeant la requete et l'exploitation de son retour.

"""
import cx_Oracle
from rshell.fileTools import file_config as _file_config
from rshell.tools.params.project import Project

# really specific environment configuration file.
ora_conf = Project().CONFIG_ORACLE_FILE


def _oracle_action(*args, condition, credentials_file=ora_conf):
    """
    Fonction generique permettant de se connecter a Oracle sur Platon en utilisant les parametres
    ora_conf.

    ATTENTION les attributs de confs sont notes en specifique, si vous changez les parametres, assurez vous de
    changer les attributs de conf si necessaire.

    :param args:
    :param condition:
    :return:
    """
    conf = _file_config(credentials_file)
    # log en premier car sinon on n'a pas ces infos dans rf
    print('Oracle connection -> user:{} - pwd:{} - {}:{}/{}'.format(conf.P_USRTRT, conf.P_PWDTRT, conf.P_HOSTTRT,
                                                                    conf.P_PORTTRT, conf.P_SIDTRT))
    # les attributs dynamiques sont notés en brut, l'ide n'aime pas ça, mais creer un intermediaire
    # prendrait des heures et obligerai à ajouter un fichier de parametres, je concidere donc la methode en specifique
    connection = cx_Oracle.Connection(conf.P_USRTRT, conf.P_PWDTRT,
                                      "{}:{}/{}".format(conf.P_HOSTTRT, conf.P_PORTTRT, conf.P_SIDTRT))
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


def delete_tables(*tables):
    """
    Supprime le contenu de chaque table de la liste.
    Effecute requete par requete.

    L'integration du nom de table dans la requete fait qu'une exception sera critique et provoquera l'arret
    du process (pour les parametres, l'excepetion n'est pas critique)
    :param tables:
    :return:
    """

    def delete(cursor, tables_to_delete):
        print("<Deleting from tables> -> {}".format(tables_to_delete))
        for table in tables_to_delete:
            print("processing table %s" % table)
            # 'DELETE * FROM x' ne marche pas.
            req = "DELETE FROM %s" % table
            cursor.execute(req)
        return None

    # execution de l'action en utilisant la fonction scope
    result = _oracle_action(tables, condition=delete)
    return result


def delete_table_partitions(table, partitions):
    """
    Supprime le contenu de chaque table de la liste.
    Effecute requete par requete.

    L'integration du nom de table dans la requete fait qu'une exception sera critique et provoquera l'arret
    du process (pour les parametres, l'excepetion n'est pas critique)
    :param table:
    :return:
    """
    def delete(cursor, partitions_table, partitions_to_delete):
        print("<Deleting from partitions> -> <Table {}> ({})".format(partitions_table, partitions_to_delete))
        for partition in partitions_to_delete:
            print("processing table %s - partition %s" % (partitions_table, partition))
            req = "DELETE %s PARTITION (%s)" % (partitions_table, partition)
            cursor.execute(req)
        return None

    # execution de l'action en utilisant la fonction scope
    result = _oracle_action(table, partitions, condition=delete)
    return result


def delete_partitions_dict(dictionnary):
    """
    Supprime les partitions d'un dictionnaire dont la clé est le nom de table
    et la valeur la liste des partitions à vider.

    Construit pour être utilisé avec le paramétrage de models.py

    :param dictionnary:
    :return:
    """
    for key in dictionnary.keys():
        delete_table_partitions(key, dictionnary.get(key))


def count_table_rows(table_to_count):
    """
    Renvoie un int.
    :param table_to_count:
    :return:
    """

    def count_rows(cursor, table):
        print("<count of table> -> %s" % table)
        # l'assignation de variable dans la preparation de requete ne peut pas se faire sur les noms de tables...
        req = "SELECT count(1) FROM %s" % table
        response = cursor.execute(req)
        # génération d'une list car le cursor n'est plus exploitable a la fermeture de la connexion
        result = [count for count in response]
        # [0] 1e ligne, [0] 1er champs, pas de dépaquetage car il n'y a qu'une ligne, qu'un champ
        print("table %s rows number -> %s" % (table, result[0][0]))
        return result[0][0]

    result = _oracle_action(table_to_count, condition=count_rows)
    return result


def select_all_from(table_to_select):
    """
    Renvoie le contenu de la table
    A utiliser avec parcimonie (log trop gros, log pas beau)
    :param table_to_select:
    :return:
    """

    def select_all(cursor, table):
        print("<selection of table> -> %s" % table)
        req = "SELECT * FROM %s" % table
        response = cursor.execute(req)
        result = [count for count in response]
        return result

    result = _oracle_action(table_to_select, condition=select_all)
    return result


def is_table_not_empty(table):
    """
    Renvoie True si la table contient au moins une ligne. Sinon False.
    :param table:
    :return:
    """

    def is_not_empty(cursor, table):
        print("<checking not empty table> -> %s" % table)
        req = "SELECT * FROM %s WHERE ROWNUM <= 1" % table
        response = cursor.execute(req)
        result = [ele for ele in response]
        if result:
            print("Table %s not empty -> True" % table)
            return True
        else:
            print("Table %s not empty -> False" % table)
            return False

    result = _oracle_action(table, condition=is_not_empty)
    return result


def raw_query(query):
    """
    Execute une requête fournie et renvoie son résultat.
    Attention! la requête est envoyée telle qu'elle, sans vérification.
    :param query:
    :return:
    """

    def make_query(cursor, query):
        print("<execute inputed query> -> %s" % query)
        response = cursor.execute(query)
        # if else None au cas ou response serait None
        result = [ele for ele in response] if response else None
        return result

    result = _oracle_action(query, condition=make_query)
    return result
