from typing import List, Dict, Tuple, Union

import pandas as pd
from pandas import DataFrame, Series
from exchange_rates import convert_date


def convert_salary(row: Series, rates: DataFrame) -> Union[float, None]:
    if pd.isnull(row['salary_from']):
        if pd.isnull(row['salary_to']):
            return None
        val = row['salary_to']
    elif pd.isnull(row['salary_to']):
        val = row['salary_from']
    else:
        val = (row['salary_to'] + row['salary_from']) / 2

    if row['salary_currency'] == 'RUR':
        return val
    if row['salary_currency'] not in list(rates.columns):
        return None

    date = convert_date(row['published_at'])
    exchange_rate = rates.loc[f'{date[0]}-{date[1]:02d}'][row['salary_currency']]
    if exchange_rate:
        return val * exchange_rate

    return False



def main(in_filename: str, rates_filename: str, out_filename: str):
    data = pd.read_csv(in_filename)
    rates = pd.read_csv(rates_filename, index_col='date')
    out_data = []

    for i, row in data.iterrows():
        salary = convert_salary(row, rates)
        if salary:
            out_data.append({'name': row['name'], 'salary': salary, 'area_name': row['area_name'],
                             'published_at': row['published_at']})

    DataFrame(out_data).to_csv(out_filename, index=False)


if __name__ == '__main__':
    main('vacancies_dif_currencies.csv', 'exchange_rates.csv', 'vacancies_full.csv')
