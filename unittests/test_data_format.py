import unittest
from ..rshell import data_format as dt

slashed_date = u"01/01/2020"
ymd_date = u"20200101"


class MyTestCase(unittest.TestCase):

    def test_date_slashed2ymd_normal_use(self):
        outgoing = dt.date_slashed2ymd(slashed_date)
        self.assertEqual(outgoing, ymd_date)

    def test_date_ymd2slashed_normal_use(self):
        outgoing = dt.date_ymd2slashed(ymd_date)
        self.assertEqual(outgoing, slashed_date)

    def test_date_slashed2ymd_bad_format(self):
        with self.assertRaises(ValueError):
            dt.date_slashed2ymd(ymd_date)

    def test_date_ymd2slashed_bad_format(self):
        with self.assertRaises(ValueError):
            dt.date_ymd2slashed(slashed_date)

    def test_date_slashed2ymd_none_arg(self):
        with self.assertRaises(AssertionError):
            dt.date_slashed2ymd(None)

    def test_date_ymd2slashed_none_arg(self):
        with self.assertRaises(AssertionError):
            dt.date_ymd2slashed(None)


class DateMetaReleaseTest(unittest.TestCase):
    def test_date_meta_release(self):
        import datetime
        self.assertIsInstance(dt.date_meta_release("2002"), datetime.datetime)


if __name__ == '__main__':
    unittest.main()
