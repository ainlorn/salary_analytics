from table import main as table_main
from stats import main as stats_main

if __name__ == '__main__':
    program = input('Вакансии/Статистика: ')
    if program == 'Вакансии':
        table_main()
    elif program == 'Статистика':
        stats_main()
    else:
        print('Неизвестная команда')
