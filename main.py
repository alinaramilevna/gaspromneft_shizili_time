import json
import csv

from tools import *

# все наборы скважин (комбинации) хранятся в .json файле для удобства их чтения и записи туда
with open('data.json', 'r') as jsonfile:
    data = json.load(jsonfile)

# try:
#     file_i = int(sorted(os.listdir('wells_csvfiles'))[-1].split('.')[0][-1]) + 1
# except IndexError as e:
#     file_i = 0

for wells in data:
    time = 61
    count_all = 2.99 * 10 ** 6
    while count_all > 2.98 * 10 ** 6:
        # Определяем параметры b и D для формулы Арпса в зависимости от того, есть ли в комбинации ППД
        d_and_b = d_and_b_ppd if wells['PPD'] else d_and_b_without_ppd
        fname = f'well_{wells["title"]}_.csv'

        # будем хранить данные в csv-таблице для удобства чтения
        with open(f'wells_csvfiles/{fname}', mode='w', encoding='utf8') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            titles = ['дебит на запуске'] + [f'{i} месяц' for i in range(1, 61)] + ['Всего']
            writer.writerow(titles)

            wells_cnt = 0
            count_all = 0

            for key_orig in wells:
                # чтобы отличать ключи с количеством скважин от других ключей
                if key_orig[0] == 'h':
                    # и берем именно число чтобы вставить в формулу
                    key = key_orig[1:]
                    wells_cnt += wells[key_orig]
                    for i in range(wells[key_orig]):
                        data_in_curr_csv = [0] * time
                        data_in_curr_csv[0] = dupuis(float(key), Ins[wells['dist']])
                        for i in range(1, time):
                            data_in_curr_csv[i] = aprs(data_in_curr_csv[0], *d_and_b[wells['dist']], i)
                        data_in_curr_csv += [sum(data_in_curr_csv)]
                        count_all += data_in_curr_csv[-1]
                        writer.writerow(data_in_curr_csv)
                else:
                    break
            writer.writerow([f'Всего: {count_all} тонн нефти'])
            wells_cnt += wells['ppd_count'] if 'ppd_count' in wells else 0
            # отношение доходов к затратам (при курсе 1 доллар США = 90,69 рублей и стоимости 1 скважины 60 млн руб)
            income = count_all // bblc * 80 * 90.69
            expenses = 60_000_000 * wells_cnt
            res = income / expenses
            writer.writerow([f'Отношение доходов к затратам: {res}'])
            writer.writerow([f'Title: {wells["title"]}'])
            if count_all > 2.98 * 10 ** 6:
                writer.writerow(['Добыча нефти превысила запасы'])
            time -= 2
        # file_i += 1
