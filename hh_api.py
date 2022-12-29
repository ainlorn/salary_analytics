from typing import List, Dict, Tuple, Union

import requests
import pandas as pd
from pandas import DataFrame, Series

time_spans = (('00:00:00', '06:00:00'), ('06:00:00', '12:00:00'), ('12:00:00', '18:00:00'), ('18:00:00', '23:59:59'))


def hh_get_vacancies(date_from: str, date_to: str) -> List:
    page = 0
    total_pages = 999

    items = []

    while page < total_pages:
        r = requests.get('https://api.hh.ru/vacancies', params={
            'date_from': date_from,
            'date_to': date_to,
            'page': 0,
            'per_page': 100
        }).json()
        items += r['items']
        total_pages = min(20, r['pages'])
        page += 1

    return items


def process_vacancies(vacancies: List[Dict]):
    return [[vacancy["name"],
             vacancy["salary"]["from"],
             vacancy["salary"]["to"],
             vacancy["salary"]["currency"],
             vacancy["area"]["name"],
             vacancy["published_at"]] for vacancy in vacancies if vacancy["salary"]]


def main(date: str):
    vacancies = []

    for date_from, date_to in time_spans:
        vacancies += hh_get_vacancies(f'{date}T{date_from}', f'{date}T{date_to}')

    DataFrame(process_vacancies(vacancies),
              columns=['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']) \
        .to_csv('hh.csv', index=False)


if __name__ == '__main__':
    main('2022-12-25')
