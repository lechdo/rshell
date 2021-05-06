# encoding: utf-8
"""
Cette librairie contient les outils de comparaison de csv.

Elle comporte 2 classes :
- Compare
- Export

Compare traite la comparaison, Exporte génère des rapports sous format excel des tableaux comparés.

.. warning::

    xlsxwriter est requis pour l'exécution de cette librairie.

"""
import csv
from os import path, mkdir
from datetime import datetime
import xlsxwriter as xlsx
from collections import namedtuple
from operator import attrgetter, sub
from functools import reduce
from rshell.rf_dependant.rf_variables import _get_current_testsuite_name
from rshell.tools.exceptions import CompareError, NotComparableError
from rshell.tools.params.project import directories_params, default_params, csv_params

#######################################################################################################################
# Paramètres                                                                                                          #
#######################################################################################################################

# Paramètres du report xlsx
###########################

REPORT_LOG_DIR = directories_params.logs
PROJECT_REPERTORY = dir_path = path.dirname(path.realpath(__file__))

ATTENDU_COLOR = '#FFFF66'
RESULTAT_COLOR = '#D15509'
# couleur des cellules valeurs différentes mais ignorées
IGNORED_VALUE_COLOR = '#C7C2C2'
ALIGN_CELL = 'center'
REPORT_FILE_EXTENSION = ".xlsx"
CELL_BORDER_SIZE = 1

#######################################################################################################################
# Partie comparaison de fichiers                                                                                      #
#######################################################################################################################

# namedtuples pour faciliter le nommage des éléments
file = namedtuple('file', 'name path data')
delta = namedtuple("delta", 'position values')
position = namedtuple('position', 'line column')
values = namedtuple('values', 'expected outgoing')
row_deltas = namedtuple('row_delta', 'line lines_lengths')


class Compare:
    @staticmethod
    def compare(expected_file_path, outgoing_file_path, columns_to_exclude=None):
        """
        Compare le contenu de deux fichiers csv. Renvoie un tableau
        qui contient l'ensemble des éléments différents entre les deux
        fichiers.

        Compare en trois étapes:
            - le nombre de lignes
            - le nombre de champs par ligne
            - chaques champs

        La méthode releve une IndexError lorsque:
            - le nombre de lignes est différent
            - le nombre de champs par ligne est différent

        :param expected_file_path:
        :param outgoing_file_path:
        :param columns_to_exclude:
        :return: [((ligne, colonne), (val fichier 1, val fichier 2))]
        """
        expected_file = file(path.split(expected_file_path)[-1], expected_file_path,
                             sorted(_file2array(expected_file_path)))
        outgoing_file = file(path.split(outgoing_file_path)[-1], outgoing_file_path,
                             sorted(_file2array(outgoing_file_path)))

        # verifie si les fichiers ont le meme nb de lignes
        if len(expected_file.data) != len(outgoing_file.data):
            raise NotComparableError("""Nombre de lignes différent entre les fichiers:
                             {} : {} ligne(s)
                             {} : {} ligne(s)"""
                                     .format(expected_file.name, len(expected_file.data),
                                             outgoing_file.name, len(outgoing_file.data)))

        lines_diffs = []
        # verifie si le nb de colonnes est != d'un fichier à l'autre pour chaque no de ligne, par soustraction
        for i in range(len(expected_file.data)):
            lines_cross = row_deltas(i + 1, (len(expected_file.data[i]), len(outgoing_file.data[i])))
            # reduce prend des fct en paramètres : https://docs.python.org/3/library/functools.html
            if reduce(sub, lines_cross.lines_lengths):
                lines_diffs.append(lines_cross)

        fmt = ["Nombre de colonnes différent entre les fichiers.", "{} différence(s).".format(len(lines_diffs)),
               "Ligne | Attendu | resultat |"]
        fmt += [("{:5} | {:7} | {:8} |".format(line, row_num1, row_num2)) for line, (row_num1, row_num2) in lines_diffs]
        if lines_diffs:
            raise NotComparableError("\n".join(fmt))

        diffs = []
        # compare chaque champs correspondants entres les fichiers. Une différence = generation d'un tuple delta dans diff[]
        for i in range(len(expected_file.data)):
            for j in range(len(expected_file.data[i])):
                if expected_file.data[i][j] != outgoing_file.data[i][j]:
                    diffs.append(
                        delta(position(i + 1, j + 1), values(expected_file.data[i][j], outgoing_file.data[i][j])))

        log_diffs = f"{len(diffs)} différence(s) répertoriée(s) entre les fichiers {expected_file.name} et " \
                    f"{outgoing_file.name}."
        log_no_diffs = f"Aucune différence répertoriée entre les fichiers {expected_file.name} et {outgoing_file.name}"

        print(log_diffs) if diffs else print(log_no_diffs)
        if columns_to_exclude and diffs:
            last_diffs = Compare.exclure_colonnes(diffs, columns_to_exclude)
            return last_diffs
        return diffs

    @staticmethod
    def exclure_differences_date_courante(differences, final_shape="%Y%m%d"):
        """
        Retire toute différence dans les champs reconnus en tant que date du jour.
        :param final_shape:
        :param differences:
        :return:
        """
        current_date = datetime.today().strftime(final_shape)
        diffs_wo_cur_date = []
        first_value = getattr('values.expected')
        # exclue le delta si la valeur expected correspond au format date
        for difference in differences:
            diffs_wo_cur_date.append(difference) if not first_value(difference).startswith(current_date) else None
        return diffs_wo_cur_date

    @staticmethod
    def exclure_colonnes(differences, column_list):
        """
        Retire toute différence relevée dans une colonne de
        la liste, parmi celles indiquée dans le tableau de différences.
        :param differences: tableau généré par le keyword Compare
        :param column_list:
        :return:
        """
        excluded_column = [(int(val)) for val in column_list]
        delta_column = attrgetter('position.column')
        diffs_wo_col_list = _exclude(differences, excluded_column, delta_column)
        print("{} différence(s) restante(s) après exclusion des lignes {}.".format(len(diffs_wo_col_list),
                                                                                   excluded_column))
        return diffs_wo_col_list

    @staticmethod
    def exclure_lignes(differences, lines_list):
        """
           Retire toute différence relevée dans une ligne de
           la liste, parmi celles indiquée dans le tableau de différences.

           .. note::

               Ce Keyword a été ajouté pour ignorer les entêtes de certains jeux de données.

           :param lines_list:
           :param differences: tableau généré par le keyword Compare
           :return:
           """
        excluded_lines = [(int(val)) for val in lines_list]
        delta_line = attrgetter("position.line")
        dif_wo_lines_list = _exclude(differences, excluded_lines, delta_line)
        print("{} différence(s) restante(s) après exclusion des lignes {}.".format(len(dif_wo_lines_list),
                                                                                   excluded_lines))
        return dif_wo_lines_list

    @staticmethod
    def exclure_champ_unique(diffs_array, line_field, column_field, log=None):
        """
        Retire un champ unique de la comparaison.

        .. note::

           Ce keyword a été réalisé pour ignorer un champ dans l'entête de certains résultats.
           Chaque ligne étant unique, un seul champ est visé dans ce cas

        :param log:
        :param diffs_array:
        :param line_field:
        :param column_field:
        :return:
        """
        diffs_wo_ufield = []
        position_field = attrgetter('position.line', 'position.column')
        unique_field = position(int(line_field), int(column_field))
        for ele in diffs_array:
            diffs_wo_ufield.append(ele) if position_field(ele) != unique_field else None
        print("Note :", log) if log else None
        print("{} différence(s) restante(s) après exclusion du champ : {}.".format(len(diffs_wo_ufield), unique_field))
        return diffs_wo_ufield

    @staticmethod
    def raise_differences(differences):
        """
        Renvoie true si le tableau de différence est vide.
        Renvoie une erreur détaillée s'il reste des différences
        :param differences:
        :return:
        """
        if differences:
            error_log = "La comparaison des fichiers contient des différence(s).\n{} différence(s) relevées"
            raise CompareError(error_log.format(len(differences)))
        else:
            print("Aucune différence entre les fichiers relevée. Comparaison concluante !!")


def _file2array(csvfile_path):
    with open(csvfile_path, 'r', newline='', encoding=default_params.ENCODING) as csvfile:
        array = csv.reader(csvfile, delimiter=csv_params.SEPARATOR)
        # transfert des données dans un itérable ne dépendant pas du module 'csv'
        return [ele for ele in array]


def _exclude(array, exclusion_list, condition):
    result = []
    # exclue le delta si sa condition est dans la liste d'exclusion
    for ele in array:
        result.append(ele) if condition(ele) not in exclusion_list else None
    return result


#######################################################################################################################
# Partie génération de fichier report                                                                                 #
#######################################################################################################################

class Export:
    @staticmethod
    def create_report_if_diffs(expected_file, outgoing_file, diff_tab):
        """
        Génère un rapport xlsx si la variable diff_tab (les différences relevées)
        est non nulle.
        """
        if diff_tab:
            Export.create_log_xlsx_compare_file(expected_file, outgoing_file, diff_tab)
        else:
            print("Aucun delta, pas de génération de report.")

    @staticmethod
    def create_log_xlsx_compare_file(expected_file, outgoing_file, diff_tab):
        """
        Renvoie un fichier xlsx dans le dossier REPORT_LOG_DIR, permettant une
        comparaison fine des deux fichiers expected_file et outgoing_file.
        Met en relief les différences relevées dans diff_tab.
        Met en gris les différences non relevées dans diff_tab (les différences
        volontairement ignorées).
        :param expected_file:
        :param outgoing_file:
        :param diff_tab:
        :return:
        """
        mkdir(REPORT_LOG_DIR) if not path.exists(
            REPORT_LOG_DIR) else None

        expected_file_tab = sorted(_file2array(expected_file))
        outgoing_file_tab = sorted(_file2array(outgoing_file))
        workbook = xlsx.Workbook(
            path.join(REPORT_LOG_DIR, _get_current_testsuite_name() + REPORT_FILE_EXTENSION))
        yellow_format = workbook.add_format({'align': ALIGN_CELL,
                                             'bg_color': ATTENDU_COLOR})
        yellow_format.set_border(CELL_BORDER_SIZE)
        orange_format = workbook.add_format({'align': ALIGN_CELL,
                                             'bg_color': RESULTAT_COLOR,
                                             'font_color': "white"})
        orange_format.set_border(CELL_BORDER_SIZE)
        grey_format = workbook.add_format({'align': ALIGN_CELL,
                                           'bg_color': IGNORED_VALUE_COLOR})
        grey_format.set_border(CELL_BORDER_SIZE)
        fmt = workbook.add_format({'align': ALIGN_CELL})
        fmt.set_border(CELL_BORDER_SIZE)

        comparesheet = workbook.add_worksheet()
        current_line = 0
        comparesheet.write(current_line, 0, "Nombres d'erreurs relevées : {}".format(len(diff_tab)))

        current_line += 1
        colonnes_concernees = []
        for ((line, column), (_, __)) in diff_tab:
            colonne = str(column)
            colonnes_concernees.append(colonne) if not (colonne in colonnes_concernees) else None
        comparesheet.write(current_line, 0, "Colonnes concernées : " + ", ".join(colonnes_concernees))

        current_line += 2
        for i in range(0, len(expected_file_tab[0]) * 2, 2):
            comparesheet.merge_range(current_line, i, current_line, i + 1, int(i / 2 + 1), fmt)

        current_line += 1
        comparesheet.name = "Compare"
        for i in range(len(expected_file_tab)):
            line_range = i + 1
            for j in range(0, len(expected_file_tab[i]) * 2, 2):
                compared = False
                if diff_tab:
                    for ((line, column), (val1, val2)) in diff_tab:
                        if line == line_range and column == j / 2 + 1:
                            comparesheet.write(current_line + i, j, val1, yellow_format)
                            comparesheet.write(current_line + i, j + 1, val2, orange_format)
                            compared = True
                if not compared:
                    if expected_file_tab[i][int(j / 2)] != outgoing_file_tab[i][int(j / 2)]:
                        comparesheet.write(current_line + i, j, expected_file_tab[i][int(j / 2)], grey_format)
                        comparesheet.write(current_line + i, j + 1, outgoing_file_tab[i][int(j / 2)], grey_format)
                    else:
                        comparesheet.merge_range(current_line + i, j, current_line + i, j + 1,
                                                 expected_file_tab[i][int(j / 2)], fmt)

        _make_simple_worksheet(expected_file_tab, "Attendu", workbook, ATTENDU_COLOR, fmt)
        _make_simple_worksheet(outgoing_file_tab, "Resultat", workbook, RESULTAT_COLOR, fmt)

        workbook.close()


def _write_simple_line(line, row_tab, worksheet, fmt=None):
    for i in range(int(len(row_tab))):
        worksheet.write(line, i, row_tab[i], fmt)


def _make_simple_worksheet(tab, worksheet_name, workbook, ws_color=None, fmt=None):
    worksheet = workbook.add_worksheet()
    worksheet.set_tab_color(ws_color)
    worksheet.name = worksheet_name
    line_range = 1
    for line in tab:
        _write_simple_line(line_range, line, worksheet, fmt)
        line_range += 1
