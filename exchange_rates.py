from typing import List, Dict, Tuple

import pandas as pd
from pandas import DataFrame
import requests


def load_exchange_rates_for_month(month: int, year: int, currencies: List[str]) -> Dict:
    response = requests.get(f'http://www.cbr.ru/scripts/XML_daily.asp?date_req=13/{month:02d}/{year}')
    data = pd.read_xml(response.text)
    result = {'date': f'{year}-{month:02d}'}

    for i, row in data.iterrows():
        if row['CharCode'] not in currencies:
            continue
        result[row['CharCode']] = float(row['Value'].replace(',', '.')) / row['Nominal']

    return result


def get_allowed_currencies(df: DataFrame) -> List[str]:
    counts = df['salary_currency'].value_counts()
    return list(counts.where(counts > 5000).dropna().index)


def convert_date(date_str: str) -> Tuple[int, int]:
    return int(date_str[:4]), int(date_str[5:7])


def main(input_file: str):
    data = pd.read_csv(input_file)

    current_date = convert_date(data['published_at'].min())
    date_end = convert_date(data['published_at'].max())
    currencies = get_allowed_currencies(data)

    results = []

    while current_date != date_end:
        print(current_date)
        results.append(load_exchange_rates_for_month(current_date[1], current_date[0], currencies))
        if current_date[1] == 12:
            current_date = (current_date[0] + 1, 1)
        else:
            current_date = (current_date[0], current_date[1] + 1)

    results_df = DataFrame(results)
    results_df.to_csv('exchange_rates.csv', index=False)


if __name__ == '__main__':
    main('vacancies_dif_currencies.csv')
