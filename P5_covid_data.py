import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import json
from urllib.request import urlopen

# source data
json_hosp = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/hospitalizace.json"
json_infect = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakazeni-vyleceni-umrti-testy.json"
path_vac = '/Users/shijunlin/Desktop/current/ockovani-pozitivity-hospitalizace-jip.xlsx' 


def get_data(url):
    response = urlopen(url)
    json_data = response.read().decode('utf-8', 'replace')
    d = json.loads(json_data)
    df = pd.json_normalize(d['data'])
    return df

d_hosp, d_infect = get_data(json_hosp), get_data(json_infect)
df_date_hosp, df_hosp, df_severe = pd.to_datetime(d_hosp['datum']), d_hosp.iloc[:, 3], d_hosp.iloc[:, 7]
df_date_infect, df_infect = pd.to_datetime(d_infect.iloc[34:, 0]), d_infect.iloc[34:, 1] - d_infect.iloc[34:, 2] - d_infect.iloc[34:, 3]
df_hosp.index = df_infect.index = df_severe.index
df_hosp_ratio = (df_hosp / df_infect)
df_severe_ratio = (df_severe / df_hosp)

df_vac = pd.read_excel(path_vac, sheet_name = None)
df_poz, df_hos, df_jip = df_vac['pozitivity'], df_vac['hospitalizace'], df_vac['jip']


x = df_date_infect
y1 = df_infect
y2 = df_hosp
y3 = df_severe
y4 = df_hosp_ratio
y5 = df_severe_ratio

i_2020 = 200 - 34
i_2021 = 549
n = 62

x_2020 = df_date_infect.iloc[i_2020 : i_2020 + n]
x_2021 = df_date_infect.iloc[i_2021 : i_2021 + n]

y4_2020 = df_hosp_ratio.iloc[i_2020 : i_2020 + n]
y4_2021 = df_hosp_ratio.iloc[i_2021 : i_2021 + n]

y5_2020 = df_severe_ratio.iloc[i_2020 : i_2020 + n]
y5_2021 = df_severe_ratio.iloc[i_2021 : i_2021 + n]

y1_2020 = df_infect.iloc[i_2020 : i_2020 + n]
y1_2021 = df_infect.iloc[i_2021 : i_2021 + n]

y2_2020 = df_hosp.iloc[i_2020 : i_2020 + n]
y2_2021 = df_hosp.iloc[i_2021 : i_2021 + n]

y3_2020 = df_severe.iloc[i_2020 : i_2020 + n]
y3_2021 = df_severe.iloc[i_2021 : i_2021 + n]

print(x_2020.head(1))
print(x_2020.tail(1))
# print(x_2021.head(1))
# print(x_2021.tail(1))

# pd.set_option('display.max_rows', None)
# print(x_2021)
# print(y4_2020.index[y4_2020 == '2021-08-15'].tolist())


def plot_infect_hosp_severe_whole():
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (14, 7))

    ax[0].plot(x, y1, 'y', label = "infected")
    ax[0].plot(x, y2, 'b', label = "hospitalised")
    ax[0].plot(x, y3, 'r', label = "severe/ICU")
    ax[1].plot(x, y4, 'b.', label = "ratio of hospitalised over infected")
    ax[1].plot(x, y5, 'r.', label = "ratio of severe/ICU over hospitalised")

    for ax0 in ax:
        ax0.set(xlabel='date')
        ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        ax0.grid()
        ax0.legend()
    ax[0].set(title="Covid Situation in Czech Republic", ylabel='no. of patients')
    ax[1].set(ylabel='ratio')
    fig.autofmt_xdate()
    plt.show()


def plot_infect_hosp_severe_parts():
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize = (15, 7))

    ax = ax.flatten()
    ax[0].plot(x_2020, y1_2020, 'y', label = "infected 2020")
    ax[0].plot(x_2020, y2_2020, 'b', label = "hospitalised 2020")
    ax[0].plot(x_2020, y3_2020, 'r', label = "severe/ICU 2020")
    ax[1].plot(x_2021, y1_2021, 'y', label = "infected 2021")
    ax[1].plot(x_2021, y2_2021, 'b', label = "hospitalised 2021")
    ax[1].plot(x_2021, y3_2021, 'r', label = "severe/ICU 2021")
    ax[2].plot(x_2020, y4_2020, 'b.', label = "ratio of hospitalised over infected 2020")
    ax[2].plot(x_2020, y5_2020, 'r.', label = "ratio of severe/ICU over hospitalised 2020")
    ax[3].plot(x_2021, y4_2021, 'bx', label = "ratio of hospitalised over infected 2021")
    ax[3].plot(x_2021, y5_2021, 'rx', label = "ratio of severe/ICU over hospitalised 2021")

    for ax0 in ax:
        ax0.set(xlabel='date', ylabel='ratio')
        ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d')) #? data period changed but not reflected in x axis tick label
        ax0.grid()
        ax0.legend()
    ax[0].set(ylim=[0,70000], title='Aug-Oct 2020')
    ax[1].set(ylim=[0,70000], title='Sep-Nov 2021')
    ax[2].set(ylim=[0,0.30], title='Aug-Oct 2020')
    ax[3].set(ylim=[0,0.30], title='Sep-Nov 2021')
    fig.autofmt_xdate()
    plt.show()

if __name__ == '__main__':
    pass
    # plot_infect_hosp_severe_whole()
    plot_infect_hosp_severe_parts()
