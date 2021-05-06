import unittest
from rshell.tools.exceptions import CompareError, NotComparableError
# l'import est réalisé après cette méthode, ce n'est certe pas une bonne pratique.
# Je l'ai conçu comme cela car la construction d'une librairie n'est pas encore au stade 'module', une bonne pratique
# demanderai beaucoup de code et de script, et ce ne sont que les TUs...
from rshell import compare as fc
from rshell.compare import Compare as c
from rshell.tools.params.project import Default

if not Default().test_mode:
    raise ValueError("MODE TEST NON ENCLENCHE, MODIFIEZ LES PARAMETRES")


class TestGetCurrentTestSuiteName(unittest.TestCase):
    def test_get_current_testsuite_name_test_mode(self):
        """
        vérifie que la méthode décorée de check_context renvoie bien un bouchon.
        :return:
        """
        self.assertEqual("_get_current_testsuite_name-plug", fc._get_current_testsuite_name())


class TestRaiseDifferences(unittest.TestCase):
    def test_raise_differences_raise_a_delta(self):
        one_delta = [fc.delta(fc.position(0, 0), fc.values("0", "0"))]
        self.assertRaises(CompareError, c.raise_differences, differences=one_delta)

    def test_raise_differences_raise_many_deltas(self):
        many_deltas = [fc.delta(fc.position(0, 0), fc.values("0", "0")) for i in range(10)]
        self.assertRaises(CompareError, c.raise_differences, differences=many_deltas)

    def test_raise_differences_no_deltas_raised(self):
        no_deltas = []
        self.assertIsNone(c.raise_differences(no_deltas))


ALL_COL_ON_SAME_VALUE = [fc.delta(fc.position(3, 1), fc.values("0", "0")) for i in range(10)]


class TestExclureColonne(unittest.TestCase):
    def test_exclure_colonne_no_exclusion(self):
        self.assertEqual(len(ALL_COL_ON_SAME_VALUE), len(c.exclure_colonnes(ALL_COL_ON_SAME_VALUE, ["10"])))

    def test_exclure_colonne_empty_diffs_list(self):
        self.assertIsInstance(c.exclure_colonnes([], ["10"]), list)

    def test_exclure_colonne_many_exclusions(self):
        twocolvalues = [fc.delta(fc.position(3, 1), fc.values("0", "0")),
                        fc.delta(fc.position(3, 2), fc.values("0", "0"))] * 3
        result = c.exclure_colonnes(twocolvalues, ["1"])
        self.assertLess(len(result), len(twocolvalues))

    def test_exclure_colonne_all_to_exclude(self):
        self.assertEqual(c.exclure_colonnes(ALL_COL_ON_SAME_VALUE, ["1"]), [])

    def test_exclure_colonne_empty_exclusion_list(self):
        self.assertEqual(c.exclure_colonnes(ALL_COL_ON_SAME_VALUE, []), ALL_COL_ON_SAME_VALUE)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
