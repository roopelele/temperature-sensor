import matplotlib.pyplot as plt
import time
import os

PATH = "/home/pi/temperature"
TIMEZONE = 3


def graph(x, y, name):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    fig.savefig(name)
    plt.close(fig)
    print("saved", name)


def main():
    int_t = int(time.time() + (3600 * (TIMEZONE - 1)))
    t = time.gmtime(int_t)
    d = time.strftime("%Y-%m-%d", t)
    idx = 0
    while True:
        filename = f"{PATH}/logs/{d}_{idx}"
        if not os.path.exists(filename):
            break
        with open(filename, "r") as infile:
            data = infile.read().split("\n")
        x_values = []
        y_values = []
        for line in data:
            a = line.split("=")
            if len(a) != 2:
                continue
            temp = a[0].split(":")
            x_values.append(float(temp[0]) + (float(temp[1]) / 60))
            y_values.append(float(a[1]))
            y_list = [0] * len(y_values)
            for i in range(0, len(y_values)):
                j = min(10, i)
                y_list[i] = sum(y_values[i - j:i + 1]) / (j + 1)
        graph(x_values, y_list, f"{PATH}/graphs/{d}_{idx}.png")
        idx += 1


main()
