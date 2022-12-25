import multiprocessing as mp
import os
from stats import DataSetReader, MeanRepresentation, currency_to_rub


def process_start(q: mp.Queue, vac, *files):
    for file in files:
        dataset = DataSetReader(file).read()
        year = int(dataset.vacancies_objects[0].published_at[:4])

        avg_salary = MeanRepresentation()
        avg_salary_filtered = MeanRepresentation()
        count = 0
        count_filtered = 0

        for v in dataset.vacancies_objects:
            salary = int((float(v.salary.salary_to) + float(v.salary.salary_from)) / 2
                         * currency_to_rub[v.salary.salary_currency])
            avg_salary.add(salary)
            count += 1
            if vac in v.name:
                count_filtered += 1
                avg_salary_filtered.add(salary)

        q.put((year, (int(avg_salary), int(avg_salary_filtered), count, count_filtered)))


def main(csv_dir, selected_vacancy):
    files = os.listdir(csv_dir)
    process_count = mp.cpu_count() // 2

    process_batches = []
    for i in range(process_count):
        process_batches.append([])

    for i, file in enumerate(files):
        process_batches[i % process_count].append(os.path.join(csv_dir, file))

    q = mp.Queue()

    processes = []
    for proc_data in process_batches:
        p = mp.Process(target=process_start, args=(q, selected_vacancy, *proc_data))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    results = []
    while q.qsize() != 0:
        results.append(q.get(block=False))
    results.sort(key=lambda x: x[0])

    salary_dynamic = dict(map(lambda x: (x[0], x[1][0]), results))
    salary_dynamic_filtered = dict(map(lambda x: (x[0], x[1][1]), results))
    count_dynamic = dict(map(lambda x: (x[0], x[1][2]), results))
    count_dynamic_filtered = dict(map(lambda x: (x[0], x[1][3]), results))

    print('Динамика уровня зарплат по годам:', salary_dynamic)
    print('Динамика количества вакансий по годам:', count_dynamic)
    print('Динамика уровня зарплат по годам для выбранной профессии:', salary_dynamic_filtered)
    print('Динамика количества вакансий по годам для выбранной профессии:', count_dynamic_filtered)


if __name__ == '__main__':
    main('csv_split', 'Аналитик')
