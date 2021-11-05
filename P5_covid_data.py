import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from unidecode import unidecode

driver = webdriver.Chrome()
# driver.implicitly_wait(10)

driver.get('https://onemocneni-aktualne.mzcr.cz/covid-19')

path_hosp = '//*[@id="main"]/div[3]/div[4]/div[7]/div[2]/div[1]/div'

df = pd.read_html(driver.find_element(By.XPATH, path_hosp).get_attribute('outerHTML'))[0]
print(df.info())
driver.quit()
# print(df.iloc[:, 1:3])

# response = urlopen("https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/hospitalizace.json")
# json_data = response.read().decode('utf-8', 'replace')

# d = json.loads(json_data)
# df = pd.json_normalize(d['data'])
# df['datum'] = pd.to_datetime(df['datum'])
# df = df.set_index('datum')

# print (df.info())

# # change figure size
# print(plt.rcParams.get('figure.figsize'))
fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 10
fig_size[1] = 5
plt.rcParams["figure.figsize"] = fig_size


def plot_graph(x, y, xlabel, ylabel, title=''):
    plt.plot(x, y, 'b')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    # plt.xticks(rotation=90)
    plt.show()

x = pd.to_datetime(df.iloc[:, 0])
# y = pd.Series(unidecode(df.iloc[:, 1]).str.replace(' ', ''))
y = df.iloc[:, 1].apply(lambda x: (unidecode(x).replace(' ','')))
# pd.set_option("display.max_rows", None, "display.max_columns", None)
# print(y)
y = pd.to_numeric(y)
xlabel = 'date'
ylabel = 'no. of people hospitalised'


# plot_graph(x, y, xlabel, ylabel)


# s = pd.Series(['319', '2 489'])
# s = pd.to_numeric(s.str.replace(' ', ''))
# print(s)