# coding: utf-8
import unittest
from rshell.tools.params.project import default_params, directories_params, project_params, csv_params, \
    cooker_params
from os import path, mkdir, rmdir


class DefaultParamsTestsCases(unittest.TestCase):
    def test_encoding_get_string_value(self):
        self.assertIsInstance(default_params.encoding, str)

    def test_testmode_get_boolean_value(self):
        self.assertIsInstance(default_params.test_mode, bool)


class DirectoriesParamsTestsCases(unittest.TestCase):
    def test_parametersdir_get_string_value(self):
        self.assertIsInstance(directories_params.parameters, str)

    def test_confdir_get_string_value(self):
        self.assertIsInstance(directories_params.configuration, str)

    def test_toolsdir_get_string_value(self):
        self.assertIsInstance(directories_params.tools, str)

    def test_suitesdir_get_string_value(self):
        self.assertIsInstance(directories_params.suites, str)

    # def test_datadir_get_string_value(self):
    #     self.assertIsInstance(directories_params.data, str)

    def test_logsdir_get_string_value(self):
        self.assertIsInstance(directories_params.logs, str)

    def test_logsdir_get_existing_path(self):
        # logs est généré, on teste la génération
        try:
            mkdir(directories_params.logs)
        except Exception:
            pass
        self.assertEqual(path.exists(directories_params.logs), True)
        # on le détruit ensuite pour retrouver la situation initiale
        rmdir(directories_params.logs)

    def test_keywordsdir_get_string_value(self):
        self.assertIsInstance(directories_params.keywords, str)

    def test_settingsdir_get_string_value(self):
        self.assertIsInstance(directories_params.settings, str)


class CsvParamsTestCases(unittest.TestCase):
    def test_separator_get_character_value(self):
        self.assertIsInstance(csv_params.separator, str)
        self.assertEqual(len(csv_params.separator), 1)

    def test_commentcharacter_get_character_value(self):
        self.assertIsInstance(csv_params.comment_character, str)
        self.assertEqual(len(csv_params.comment_character), 1)


class CookerParamsTestCases(unittest.TestCase):
    def test_clusternamemaxlength_get_integer_value(self):
        self.assertIsInstance(cooker_params.cluster_name_max_length, int)

    def test_testsuitenamemaxlength_get_integer_value(self):
        self.assertIsInstance(cooker_params.test_suite_name_max_length, int)

    def test_testscriptextension_get_string_value(self):
        self.assertIsInstance(cooker_params.test_script_extension, str)

    def test_callerseparator_get_character_value(self):
        self.assertIsInstance(cooker_params.caller_separator, str)
        self.assertEqual(len(cooker_params.caller_separator), 1)


# TODO tests de ParametersParams
# TODO tests de VenvParams

if __name__ == '__main__':
    unittest.main()
