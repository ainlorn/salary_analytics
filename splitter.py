import csv
import os


def main(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        try:
            header = reader.__next__()
        except StopIteration:
            raise Exception("Пустой файл")
        date_col_idx = header.index('published_at')
        years = {}
        for line in reader:
            year = line[date_col_idx][:4]
            if year not in years:
                years[year] = []
            years[year].append(line)

        for year in years:
            with open(os.path.join('csv_split', f'{year}.csv'), 'w', newline='', encoding='utf-8-sig') as of:
                writer = csv.writer(of)
                writer.writerow(header)
                writer.writerows(years[year])


if __name__ == '__main__':
    main('vacancies.csv')
