# -*- coding: utf-8 -*-
"""
Module de gestion des formats de données, notamment les dates.

.. note::

    Ce module a pour vocation de simplifier l'utilisation de données dans robotframwork,
    dont la valeur susciterait un formattage ou une génération.
    L'idée est d'obtenir des keywords très spécifiques mais permettant une seule action dans
    robot pour l'obtenir.


"""
from datetime import datetime
from functools import partial
from dateutil.relativedelta import relativedelta
from collections import namedtuple
from rshell.tools.params.project import Project

release = Project().META_RELEASE


def _data_value_error_log(wrong_value, good_value):
    log = """
Le format {} n'est pas correct,
le format requis est {}""".format(wrong_value, good_value)
    raise ValueError(log)


def _format_date(str_date, incoming_fmt):
    """
    Convertit une date string en instance datetime.
    Permet de reformatter la date entrée sous n'importe quel format à l'envie.

    Cette méthode est interne, elle est un outil pour passer d'un string de date
    à un objet de type datetime.

    :param str_date: date en string
    :param incoming_fmt: format d'entrée
    :param outgoing_format:
    :return:
    """
    assert isinstance(str_date, str), "La date dois être au format string"
    try:
        datetimed_date = datetime.strptime(str_date, incoming_fmt)
        return datetimed_date
    except ValueError:
        _data_value_error_log(str_date, incoming_fmt)


# date entrante en DD/MM/YYYY
slashed_strdate2datetime = partial(_format_date, incoming_fmt="%d/%m/%Y")
# date entrante en YYYMMDD
ymd_strdate2datetime = partial(_format_date, incoming_fmt="%Y%m%d")


def date_slashed2ymd(strdate):
    """
    Convertit une date string DD/MM/YYYY en string YYYYMMDD

    :param strdate: date sous format string DD/MM/YYYY
    :return: date sous format string YYYYMMDD
    """
    date_obj = slashed_strdate2datetime(strdate)
    return datetime.strftime(date_obj, "%Y%m%d")


def date_ymd2slashed(strdate):
    """
    Convertit une date string YYYYMMDD en string DD/MM/YYYY

    :param strdate: date sous format string YYYYMMDD
    :return: date sous format string DD/MM/YYYY
       """
    date_obj = ymd_strdate2datetime(strdate)
    return datetime.strftime(date_obj, "%d/%m/%Y")


def date_mep():
    date_obj = datetime.strptime(release, "%y%m")
    return date_obj


def date_testing():
    """
    Renvoie un objet datetime de la méta release, avec jour = 01.
    La metarelease est calculée à partir du paramètre indiqué dans config.ini

    :param release:
    :return:
    """
    date_obj = datetime.strptime(release, "%y%m")
    # date_release = datetime(year=date_obj.year, month=(date_obj.month + 7) % 12, day=1)
    date_release = date_obj - relativedelta(months=5)
    print("date version      ->", date_obj.strftime("%m/%Y"))
    print("date Meta release ->", date_release.strftime("%m/%Y"))
    return date_release


def tuple_date_meta_release():
    """
    Renvoie un namedtuple de la méta release avec éléments jours, mois et années.
    :param release:
    :return:
    """
    dmr = date_testing()
    # création d'un namedtuple pour la lisibilité des données dans rf.
    dmr_format = namedtuple('meta_relaease', 'day month year')
    return dmr_format(day=dmr.day, month=dmr.month, year=dmr.year)


def date_after_meta_release(months, days=1, date_format="%Y%m%d"):
    """
    renvoie une date au format demandé avec le delta en mois et jours par rapport à la Meta Release.
    days à défaut à 1, format à défaut à YYYYMMDD

    :param months:
    :param release:
    :param date_format:
    :param days:
    :return:
    """
    assert int(months), "months doit être un numérique"
    assert 31 >= int(days) >= 1, \
        "days doit être un numérique compris entre 1 et 31. Attentions aux valeurs entre 28 et 31 !! : %s" % days
    print("format date with\ndays -> %s\nmonths -> %s" % (days, months))
    release = date_meta_release()
    new_date = release + relativedelta(months=int(months), days=int(days) - 1)
    return new_date.strftime(date_format)
