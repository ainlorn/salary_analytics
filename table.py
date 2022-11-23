import csv
import functools
import re
import collections

import prettytable
from prettytable import PrettyTable

table_fields = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания', 'Оклад',
                'Название региона', 'Дата публикации вакансии']

value_replacements = {
    'premium': {
        'False': 'Нет',
        'True': 'Да',
        'FALSE': 'Нет',
        'TRUE': 'Да'
    },
    'salary_gross': collections.defaultdict(lambda: 'С вычетом налогов', {
        'True': 'Без вычета налогов'
    }),
    'salary_currency': {
        "AZN": "Манаты",
        "BYR": "Белорусские рубли",
        "EUR": "Евро",
        "GEL": "Грузинский лари",
        "KGS": "Киргизский сом",
        "KZT": "Тенге",
        "RUR": "Рубли",
        "UAH": "Гривны",
        "USD": "Доллары",
        "UZS": "Узбекский сум"
    },
    'experience_id': {
        "noExperience": "Нет опыта",
        "between1And3": "От 1 года до 3 лет",
        "between3And6": "От 3 до 6 лет",
        "moreThan6": "Более 6 лет"
    }
}


def filter_skills(v, s):
    skills = v.key_skills
    return all([skill in skills for skill in s.split(', ')])


filter_functions = {
    'Название': lambda v, s: v.name == s,
    'Описание': lambda v, s: v.description == s,
    'Компания': lambda v, s: v.employer_name == s,
    'Название региона': lambda v, s: v.area_name == s,
    'Оклад': lambda v, s: int(v.salary.salary_to) >= int(s) >= int(v.salary.salary_from),
    'Дата публикации вакансии': lambda v, s: re.sub(r'^(\d{4})-(\d{2})-(\d{2}).*$', r'\3.\2.\1',
                                                    v.published_at) == s,
    'Навыки': filter_skills,
    'Идентификатор валюты оклада': lambda v, s: value_replacements['salary_currency'][v.salary.salary_currency] == s,
    'Опыт работы': lambda v, s: value_replacements['experience_id'][v.experience_id] == s,
    'Премиум-вакансия': lambda v, s: value_replacements['premium'][v.premium] == s,
}

currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}

experience_ids = list(value_replacements['experience_id'].keys())

sorting_keys = {
    'Название': lambda v: v.name,
    'Описание': lambda v: v.description,
    'Компания': lambda v: v.employer_name,
    'Название региона': lambda v: v.area_name,
    'Оклад': lambda v: (float(v.salary.salary_from) + float(v.salary.salary_to)) / 2 * currency_to_rub[
        v.salary.salary_currency],
    'Дата публикации вакансии': lambda v: v.published_at,
    'Навыки': lambda v: len(v.key_skills),
    'Идентификатор валюты оклада': lambda v: value_replacements['salary_currency'][v.salary.salary_currency],
    'Опыт работы': lambda v: experience_ids.index(v.experience_id),
    'Премиум-вакансия': lambda v: value_replacements['premium'][v.premium],
}


class DataSet:
    def __init__(self, file_name, vacancies_objects):
        self.file_name = file_name
        self.vacancies_objects = vacancies_objects


class Options:
    def __init__(self):
        self.file_name = None
        self.start = None
        self.end = None
        self.columns = None
        self.sorting_params = (None, None)
        self.filtering_params = (None, None)


class InputReader:
    def __init__(self):
        self.errors = []

    def read(self):
        opts = Options()
        opts.file_name = input('Введите название файла: ')
        opts.filtering_params = self.read_filter_params()
        opts.sorting_params = self.read_sorting_params()
        opts.start, opts.end = self.read_start_end()
        opts.columns = self.read_columns()
        return opts

    def read_filter_params(self):
        line = input('Введите параметр фильтрации: ')
        if line:
            if ': ' not in line:
                self.errors.append('Формат ввода некорректен')
                return None, None
            spl = line.split(': ')
            _filter = spl[0]
            filter_str = spl[1]
            if _filter not in filter_functions:
                self.errors.append('Параметр поиска некорректен')
                return None, None
            return _filter, filter_str
        return None, None

    def read_start_end(self):
        start = None
        end = None
        line = input('Введите диапазон вывода: ')
        if line:
            spl = line.split(' ')
            start = int(spl[0]) - 1
            if len(spl) == 2:
                end = int(spl[1]) - 1
        return start, end

    def read_columns(self):
        line = input('Введите требуемые столбцы: ')
        if line:
            columns = line.split(', ')
            return columns
        return None

    def read_sorting_params(self):
        param = input('Введите параметр сортировки: ')
        if param == '':
            param = None
        elif param not in sorting_keys:
            param = None
            self.errors.append('Параметр сортировки некорректен')
        reverse = input('Обратный порядок сортировки (Да / Нет): ')
        if reverse == 'Да':
            reverse = True
        elif reverse == 'Нет' or reverse == '':
            reverse = False
        else:
            reverse = None
            self.errors.append('Порядок сортировки задан некорректно')
        return param, reverse


class TableGenerator:
    def __init__(self, options, dataset):
        self.options = options
        self.vacancies = list(dataset.vacancies_objects)
        self._error_msg = None
        self._filter_vacancies()
        self._sort_vacancies()
        self._table = self._make_table()

    def _sort_vacancies(self):
        sort_by = self.options.sorting_params[0]
        reverse = self.options.sorting_params[1]
        if sort_by:
            self.vacancies.sort(key=sorting_keys[sort_by], reverse=reverse)

    def _filter_vacancies(self):
        _filter = self.options.filtering_params[0]
        filter_str = self.options.filtering_params[1]
        if _filter:
            func = functools.partial(filter_functions[_filter], s=filter_str)
            self.vacancies[:] = filter(func, self.vacancies)
            if len(self.vacancies) == 0:
                self._error_msg = 'Ничего не найдено'

    @staticmethod
    def _format_num_str(num_str):
        return f'{int(float(num_str)):,}'.replace(',', ' ')

    @staticmethod
    def _format_vacancy(v):
        _from = TableGenerator._format_num_str(v.salary.salary_from)
        _to = TableGenerator._format_num_str(v.salary.salary_to)
        _curr = value_replacements["salary_currency"][v.salary.salary_currency]
        _gross = value_replacements["salary_gross"][v.salary.salary_gross]
        match = re.match(r'^(\d{4})-(\d{2})-(\d{2}).*$', v.published_at)

        formatted_vacancy = {
            'Название': v.name,
            'Описание': v.description,
            'Навыки': '\n'.join(v.key_skills),
            'Опыт работы': value_replacements['experience_id'][v.experience_id],
            'Премиум-вакансия': value_replacements['premium'][v.premium],
            'Компания': v.employer_name,
            'Оклад': f'{_from} - {_to} ({_curr}) ({_gross})',
            'Название региона': v.area_name,
            'Дата публикации вакансии': f'{match[3]}.{match[2]}.{match[1]}'
        }
        return formatted_vacancy

    def _make_table(self):
        table = PrettyTable()
        table.field_names = table_fields
        table.align = 'l'
        table.max_width = 20
        table.hrules = prettytable.ALL
        i = 1
        if len(self.vacancies) == 0:
            if not self._error_msg:
                self._error_msg = 'Нет данных'

        for v in self.vacancies:
            formatted = TableGenerator._format_vacancy(v)
            table.add_row([str(i), *map(lambda x: x if len(x) <= 100 else f'{x[:100]}...', formatted.values())])
            i += 1
        return table

    def print(self):
        if self._error_msg:
            print(self._error_msg)
            return

        kwargs = {}
        if self.options.start:
            kwargs['start'] = self.options.start
        if self.options.end:
            kwargs['end'] = self.options.end
        if self.options.columns:
            kwargs['fields'] = ['№', *self.options.columns]
        print(self._table.get_string(**kwargs))


class Vacancy:
    def __init__(self, name, description, key_skills, experience_id, premium, employer_name, salary, area_name,
                 published_at):
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at


class Salary:
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency


class DataSetReader:
    def __init__(self, path):
        self.path = path

    def read(self):
        csv = self._read_csv()
        lines = self._parse_csv(*csv)
        return self._convert_to_dataset(lines)

    def _read_csv(self):
        with open(self.path, newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            try:
                header = reader.__next__()
            except StopIteration:
                raise Exception("Пустой файл")
            lines = []
            for line in reader:
                lines.append(line)
            return header, lines

    def _parse_csv(self, header, lines):
        lines_clean = []
        for line in lines:
            if '' in line or len(line) != len(header):
                continue
            d = {}
            for i, item in enumerate(line):
                item = item.replace('\r', '').split('\n')
                for j, sub in enumerate(item):
                    item[j] = re.sub(' +', ' ',
                                     re.sub('<.*?>', '', sub.replace('\u2002', ' ').replace('\u00a0', ' '))).strip()
                if len(item) > 1:
                    d[header[i]] = '\n'.join(item)
                else:
                    d[header[i]] = item[0]
            lines_clean.append(d)
        return lines_clean

    def _convert_to_dataset(self, lines):
        vacancies = []
        for l in lines:
            key_skills = l['key_skills'].split('\n')
            salary = Salary(l['salary_from'], l['salary_to'], l['salary_gross'], l['salary_currency'])
            vacancy = Vacancy(l['name'], l['description'], key_skills, l['experience_id'], l['premium'],
                              l['employer_name'], salary, l['area_name'], l['published_at'])
            vacancies.append(vacancy)
        return DataSet(self.path, vacancies)


def main():
<<<<<<< HEAD
    reader = InputReader()  # abcdef
=======
    reader = InputReader()  # conflict!!!
>>>>>>> develop
    opts = reader.read()
    if reader.errors:
        print('\n'.join(reader.errors))
        return

    try:
        dataset = DataSetReader(opts.file_name).read()
    except Exception as e:
        print(e.args[0])
        return

    TableGenerator(opts, dataset).print()


if __name__ == '__main__':
    main()
