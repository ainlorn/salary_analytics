from unittest import TestCase
from table import Salary, convert_date


class SalaryTests(TestCase):
    def test_salary_type(self):
        self.assertEqual(type(Salary(10, 20, False, 'RUR')).__name__, 'Salary')

    def test_salary_from(self):
        self.assertEqual(Salary(10, 20, False, 'RUR').salary_from, 10)

    def test_salary_to(self):
        self.assertEqual(Salary(10, 20, False, 'RUR').salary_to, 20)

    def test_salary_currency(self):
        self.assertEqual(Salary(10, 20, False, 'RUR').salary_currency, 'RUR')

    def test_salary_in_rub_int(self):
        self.assertEqual(Salary(10, 20, False, 'RUR').get_salary_in_rub(), 15.0)

    def test_salary_in_rub_first_float(self):
        self.assertEqual(Salary(10.0, 20, False, 'RUR').get_salary_in_rub(), 15.0)

    def test_salary_in_rub_second_float(self):
        self.assertEqual(Salary(10, 30.0, False, 'RUR').get_salary_in_rub(), 20.0)

    def test_salary_eur_in_rub(self):
        self.assertEqual(Salary(10, 30, False, 'EUR').get_salary_in_rub(), 1198.0)

    def test_salary_kzt_in_rub(self):
        self.assertEqual(Salary(1000, 2000, False, 'KZT').get_salary_in_rub(), 195.0)

    def test_salary_asn_in_rub(self):
        self.assertEqual(Salary(2000, 4000, False, 'AZN').get_salary_in_rub(), 107040.0)


class DateConverterTests(TestCase):
    def test_date_convert_correct(self):
        self.assertListEqual(convert_date('2022-12-25'), [2022, 12, 25])

    def test_date_convert_month_too_small(self):
        with self.assertRaises(Exception):
            convert_date('2022-00-25')

    def test_date_convert_month_too_big(self):
        with self.assertRaises(Exception):
            convert_date('2022-13-25')

    def test_date_convert_day_too_small(self):
        with self.assertRaises(Exception):
            convert_date('2022-12-00')

    def test_date_convert_day_too_big(self):
        with self.assertRaises(Exception):
            convert_date('2022-12-99')
