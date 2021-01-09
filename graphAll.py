import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

PATH = "/home/pi/temperature/"
TIMEZONE = 3

def main():
  filename = PATH + "logs/2020.csv"
  with open(filename, "r") as file:
    data = file.read().split("\n")
  x_values = []
  minimum = []
  maximum = []
  average = []
  for line in data:
    a = line.split(",")
    if len(a) != 4:
      continue
    try:
      x_values.append(dt.datetime.strptime(a[0], "%Y-%m-%d").date())
    except ValueError:
      continue
    average.append(float(a[1]))
    maximum.append(float(a[2]))
    minimum.append(float(a[3]))
  plt.figure()
  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
  plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
  plt.plot_date(x_values, average, 'g-')
  plt.plot_date(x_values, maximum, 'r-')
  plt.plot_date(x_values, minimum, 'b-')
  plt.savefig(PATH + "graphs/2020.png")



main()
