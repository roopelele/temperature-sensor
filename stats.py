import time
from os import listdir, path

PATH = "/home/pi/temperature"
TIMEZONE = 3


def average(value_list):
    total = 0.0
    amount = 0
    for value in value_list:
        total += value
        amount += 1
    return round(total / amount, 3)


def get_date():
    int_t = int(time.time() + (3600 * (TIMEZONE - 2)))
    t = time.gmtime(int_t)
    return time.strftime("%Y-%m-%d", t)


def calc_stats(filename):
    with open(filename, "r") as file:
        data = file.readlines()
    temps = []
    for row in data:
        l = row.split('=')
        if len(l) == 2:
            temps.append(float(l[1]))
    if len(temps) == 0:
        print("len(temps) == 0")
        return
    save_data = [filename.split('/')[-1], str(average(temps)), str(max(temps)), str(min(temps))]
    save_file = f"{PATH}/logs/{filename.split('/')[-1][:4]}.csv"
    if not path.isfile(save_file):
        with open(save_file, "w") as outfile:
            outfile.write("DATE:AVG,MAX,MIN\n")
    with open(save_file, 'a') as outfile:
        outfile.write(",".join(save_data) + "\n")


def calc_all():
    files = listdir(PATH + "/logs")
    files.sort()
    for filename in files:
        if filename in ["CURRENT.json", "2020.txt"]:
            continue
        calc_stats(PATH + "/logs/" + filename)


def main():
    filename = f"{PATH}/logs/{get_date()}"
    calc_stats(filename)


main()
