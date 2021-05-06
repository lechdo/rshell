# -*- coding: utf-8 -*-
import unittest
import rshell.param_handler as ph
from os import path
import multiprocessing
import time
from rshell.tools.exceptions import NotConfiguredError, ConfigContentError


CONF_DIR = path.dirname(__file__)
ko_dummyfile_conf = path.join(CONF_DIR, "dummy4test_ko.cfg")
ok_dummyfile_conf = path.join(CONF_DIR, "dummy4test_ok.cfg")


class ConfigTuplesTestsCases(unittest.TestCase):
    def test__contextual_config_tuple_existing_arg_path(self):
        result = ph._contextual_config_tuple(ko_dummyfile_conf)
        # mro renvoie la hierarchie des type, 0 est le namedtuple, 1 tuple si test concluant
        self.assertEqual(result.mro()[1], tuple)

    def test__contextual_config_tuple_non_existing_arg_path(self):
        with self.assertRaises(NotConfiguredError):
            ph._contextual_config_tuple("DoesNotExist.cfg")

    def test__contextual_config_tuple_non_path_arg(self):
        with self.assertRaises(TypeError):
            ph._contextual_config_tuple(None)

    def test_conf_file2params_tuples_conf_path_exist(self):
        self.assertTrue(ph.conf_file2params_tuples(ok_dummyfile_conf))

    def test_conf_file2params_tuples_conf_path_does_not_exist(self):
        with self.assertRaises(SyntaxError):
            ph.conf_file2params_tuples("DoesNotExist.cfg")

    def test_conf_file2params_tuples_missing_one_data(self):
        with self.assertRaises(ConfigContentError):
            ph.conf_file2params_tuples(ko_dummyfile_conf)

    def test_get_config_normal_use(self):
        NotImplementedError()

    def test_get_config_key_does_not_exist(self):
        NotImplementedError()


class FlowFunctionsTestsCases(unittest.TestCase):
    def test_check_flow_until_it_match_while_loop_working(self):
        # TODO permettre le changement de DIR_CONF pour obtenir le path had'oc
        processing = multiprocessing.Process(target=ph.check_flow_until_it_match,
                                             name="check_flow_until_it_match",
                                             args=("DummyKey",))
        try:
            processing.start()
            # ph.CONF_DIR = "../Conf"
            # 30 secs, jusqu'à 6 boucles, suffisant pour constater qu'il le fait.
            time.sleep(30)
            processing.terminate()
        except SyntaxError:
            processing.terminate()
            self.fail("check_flow_until_it_match -> Exception before time out!")


if __name__ == '__main__':
    unittest.main()
