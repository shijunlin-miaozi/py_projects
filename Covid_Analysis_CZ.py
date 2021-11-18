import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import json
import os
import time
import webbrowser
from urllib.request import urlopen
from datetime import datetime, timedelta, date


# source data
json_hosp = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/hospitalizace.json"
json_infect = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakazeni-vyleceni-umrti-testy.json"
path_vac = '/Users/shijunlin/Desktop/current/ockovani-pozitivity-hospitalizace-jip.xlsx'


def update_vac_file():
    # page to download vaccine data: https://data.nzis.cz/news-detail/cs/48-covid-19-nove-otevrene-datove-sady-s-ohledem-na-vykazana-ockovani/
    url = "https://share.uzis.cz/s/Ex8j29jwLwTQz5c/download"
    filename, desktop = 'ockovani-pozitivity-hospitalizace-jip.xlsx', "/Users/shijunlin/Desktop/"
    webbrowser.open_new(url)
    time.sleep(1)
    os.replace(desktop + filename, desktop + "current/" + filename)
    print(f'file updated at {datetime.now()}')


def get_json_data(url):
    response = urlopen(url)
    json_data = response.read().decode('utf-8', 'replace')
    d = json.loads(json_data)
    df = pd.json_normalize(d['data'])
    return df


# cleansing data for graphs
d_hosp, d_infect = get_json_data(json_hosp), get_json_data(json_infect).iloc[34:] # data start from 2020-Mar-01

df_date_hosp, df_hosp, df_severe = pd.to_datetime(d_hosp['datum']), d_hosp["pocet_hosp"], d_hosp["stav_tezky"]
df_date_infect, df_infect, df_infect_new = pd.to_datetime(d_infect["datum"]), d_infect["kumulativni_pocet_nakazenych"] - d_infect["kumulativni_pocet_vylecenych"] - d_infect["kumulativni_pocet_umrti"], d_infect["prirustkovy_pocet_nakazenych"]

df_date_infect.index = df_infect.index = df_infect_new.index = df_hosp.index

df_hosp_ratio = (df_hosp / df_infect)
df_severe_ratio = (df_severe / df_hosp)

df_vac = pd.read_excel(path_vac, sheet_name = None)
df_poz, df_hos, df_jip = df_vac['pozitivity'], df_vac['hospitalizace'], df_vac['jip']

cutoff = 2021, 9, 1
df_poz = df_poz[(df_poz['od'].dt.date >= date(*cutoff))]
df_hos = df_hos[(df_hos['od'].dt.date >= date(*cutoff))]
df_jip = df_jip[(df_jip['od'].dt.date >= date(*cutoff))]

start_d, end_d = df_poz['od'].min(), df_poz['od'].max() + timedelta(days=6)

df_poz = df_poz.assign(age = df_poz['vek_kategorie'].apply(lambda x: x.split('-')[0] if len(x.split('-')[0]) < 2 else x.split('-')[0][:2]).values)
df_hos = df_hos.assign(age = df_hos['vek_kategorie'].apply(lambda x: x.split('-')[0] if len(x.split('-')[0]) < 2 else x.split('-')[0][:2]).values)
df_jip = df_jip.assign(age = df_jip['vek_kategorie'].apply(lambda x: x.split('-')[0] if len(x.split('-')[0]) < 2 else x.split('-')[0][:2]).values)

# for age_gp = ['0-24', '25-64', '65+']
# df_poz = df_poz.assign(age_gp = df_poz['age'].apply(lambda x: 'unknown' if x == 'ne' else '0-24' if int(x) < 25 else '65+' if int(x) > 64 else '25-64').values)
# df_hos = df_hos.assign(age_gp = df_hos['age'].apply(lambda x: 'unknown' if x == 'ne' else '0-24' if int(x) < 25 else '65+' if int(x) > 64 else '25-64').values)
# df_jip = df_jip.assign(age_gp = df_jip['age'].apply(lambda x: 'unknown' if x == 'ne' else '0-24' if int(x) < 25 else '65+' if int(x) > 64 else '25-64').values)

# for age_gp = ['0-14', '15-24', '25-44', '45-64', '65+']
df_poz = df_poz.assign(age_gp = df_poz['age'].apply(lambda x: 'unknown' if x == 'ne' else '0-14' if int(x) < 15 else '65+' if int(x) > 64 else '15-24' if int(x) < 25 else '25-44' if int(x) < 45 else '45-64').values)
df_hos = df_hos.assign(age_gp = df_hos['age'].apply(lambda x: 'unknown' if x == 'ne' else '0-14' if int(x) < 15 else '65+' if int(x) > 64 else '15-24' if int(x) < 25 else '25-44' if int(x) < 45 else '45-64').values)
df_jip = df_jip.assign(age_gp = df_jip['age'].apply(lambda x: 'unknown' if x == 'ne' else '0-14' if int(x) < 15 else '65+' if int(x) > 64 else '15-24' if int(x) < 25 else '25-44' if int(x) < 45 else '45-64').values)

df_poz_bydate, df_hos_bydate, df_jip_bydate = df_poz.groupby('od').sum().sum(), df_hos.groupby('od').sum().sum(), df_jip.groupby('od').sum().sum()
df_poz_byage, df_hos_byage, df_jip_byage = df_poz.groupby('age_gp').sum(), df_hos.groupby('age_gp').sum(), df_jip.groupby('age_gp').sum()

df_poz_byage = df_poz_byage.assign(w_vac = (df_poz_byage.iloc[:, 0] - df_poz_byage.iloc[:, 1]).values)
df_hos_byage = df_hos_byage.assign(w_vac = (df_hos_byage.iloc[:, 0] - df_hos_byage.iloc[:, 1]).values)
df_jip_byage = df_jip_byage.assign(w_vac = (df_jip_byage.iloc[:, 0] - df_jip_byage.iloc[:, 1]).values)


# input data for vaccination plots(pie & bar): 
label_vac_pie = ['Without Vac', 'With 1 Shot', 'With 2 Shots', 'With Booster']

value_poz_pie = df_poz_bydate.iloc[1], df_poz_bydate.iloc[2], df_poz_bydate.iloc[3], df_poz_bydate.iloc[4]
value_hos_pie = df_hos_bydate.iloc[1], df_hos_bydate.iloc[2], df_hos_bydate.iloc[3], df_hos_bydate.iloc[4]
value_jip_pie = df_jip_bydate.iloc[1], df_jip_bydate.iloc[2], df_jip_bydate.iloc[3], df_jip_bydate.iloc[4]


label_vac_bar = ['Total', 'Without Vac', 'With Vac']

value_poz_bar = df_poz_byage.iloc[:, [0, 1, -1]].transpose()
value_hos_bar = df_hos_byage.iloc[:, [0, 1, -1]].transpose()
value_jip_bar = df_jip_byage.iloc[:, [0, 1, -1]].transpose()

for df in (value_poz_bar, value_hos_bar, value_jip_bar):
    df.index = label_vac_bar

denominator = [[sum(val), val[0], sum(val) - val[0]] for val in (value_poz_pie, value_hos_pie, value_jip_pie)]

# to print data
# pd.set_option('display.max_rows', None)
# print(value_poz_bar)
# print(value_hos_bar)
# print(value_jip_bar)


# input data for infect/hosp/severe plots(lines): 
x = df_date_infect
y1 = df_infect
y2 = df_hosp
y3 = df_severe
y4 = df_infect_new
y5 = df_hosp_ratio
y6 = df_severe_ratio

x_min, x_max = x.min(), x.max()

i_2021 = x.index.max() - 6
i_2020 = i_2021 - 383
n = 90 # compare 3-mth period data (2020 vs 2021)

x_2020 = df_date_infect.iloc[i_2020 - n : i_2020]
x_2021 = df_date_infect.iloc[i_2021 - n : i_2021]

x_2020_min, x_2020_max = x_2020.min(), x_2020.max()
x_2021_min, x_2021_max = x_2021.min(), x_2021.max()

y1_2020 = df_infect.iloc[i_2020 - n : i_2020]
y1_2021 = df_infect.iloc[i_2021 - n : i_2021]

y2_2020 = df_hosp.iloc[i_2020 - n : i_2020]
y2_2021 = df_hosp.iloc[i_2021 - n : i_2021]

y3_2020 = df_severe.iloc[i_2020 - n : i_2020]
y3_2021 = df_severe.iloc[i_2021 - n : i_2021]

y4_2020 = df_infect_new.iloc[i_2020 - n : i_2020]
y4_2021 = df_infect_new.iloc[i_2021 - n : i_2021]

y5_2020 = df_hosp_ratio.iloc[i_2020 - n : i_2020]
y5_2021 = df_hosp_ratio.iloc[i_2021 - n : i_2021]

y6_2020 = df_severe_ratio.iloc[i_2020 - n : i_2020]
y6_2021 = df_severe_ratio.iloc[i_2021 - n : i_2021]

ylim_infect_max = (max(y1_2020.max(), y1_2021.max()) * -1 // 500) * -500
ylim_ratio_max = (max(y6_2020.max(), y6_2021.max()) * -1 // 0.05) * -0.05


def plot_infect_hosp_severe_whole():
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (14, 7))

    ax[0].plot(x, y1, 'y', label = "total infected")
    ax[0].plot(x, y4, 'y:', label = "newly infected")
    ax[0].plot(x, y2, 'b', label = "hospitalised")
    ax[0].plot(x, y3, 'r', label = "severe/ICU")
    ax[1].plot(x, y5, 'b.', label = "ratio of hospitalised over total infected")
    ax[1].plot(x, y6, 'r.', label = "ratio of severe/ICU over hospitalised")

    for ax0 in ax:
        ax0.set(xlabel='date')
        ax0.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b-%d'))
        ax0.grid()
        ax0.legend()
    ax[0].set(title=f'Covid Situation in Czech Republic from {x_min: %Y-%b-%d} to {x_max: %Y-%b-%d})', ylabel='no. of patients')
    ax[1].set(ylabel='ratio')
    fig.autofmt_xdate()
    return fig


def plot_infect_hosp_severe_parts():
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize = (14, 7))

    ax = ax.flatten()
    ax[0].plot(x_2020, y1_2020, 'y', label = "total infected 2020")
    ax[0].plot(x_2020, y4_2020, 'y:', label = "newly infected 2020")
    ax[0].plot(x_2020, y2_2020, 'b', label = "hospitalised 2020")
    ax[0].plot(x_2020, y3_2020, 'r', label = "severe/ICU 2020")
    ax[1].plot(x_2021, y1_2021, 'y', label = "total infected 2021")
    ax[1].plot(x_2021, y4_2021, 'y:', label = "newly infected 2021")
    ax[1].plot(x_2021, y2_2021, 'b', label = "hospitalised 2021")
    ax[1].plot(x_2021, y3_2021, 'r', label = "severe/ICU 2021")
    ax[2].plot(x_2020, y5_2020, 'b.', label = "ratio of hospitalised over infected 2020")
    ax[2].plot(x_2020, y6_2020, 'r.', label = "ratio of severe/ICU over hospitalised 2020")
    ax[3].plot(x_2021, y5_2021, 'bx', label = "ratio of hospitalised over infected 2021")
    ax[3].plot(x_2021, y6_2021, 'rx', label = "ratio of severe/ICU over hospitalised 2021")

    for ax0 in ax:
        ax0.set(xlabel='date')
        ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        ax0.grid()
        ax0.legend()
    ax[0].set(xlim=[x_2020_min, x_2020_max], ylim=[0,ylim_infect_max], title=f'3-month data in 2020 ({x_2020_min: %b-%d} - {x_2020_max: %b-%d})', ylabel='no of patients')
    ax[1].set(xlim=[x_2021_min, x_2021_max], ylim=[0,ylim_infect_max], title=f'3-month data in 2021 ({x_2021_min: %b-%d} - {x_2021_max: %b-%d})', ylabel='no of patients')
    ax[2].set(xlim=[x_2020_min, x_2020_max], ylim=[0,ylim_ratio_max], ylabel='ratio')
    ax[3].set(xlim=[x_2021_min, x_2021_max], ylim=[0,ylim_ratio_max], ylabel='ratio')
    fig.autofmt_xdate()
    return fig


def plot_vac():
    fig, ax = plt.subplots(nrows=2, ncols=3, figsize = (14, 7))
    
    ax = ax.flatten()
    ax[0].pie(value_poz_pie, labels = label_vac_pie, autopct = '%1.0f%%')
    ax[1].pie(value_hos_pie, labels = label_vac_pie, autopct = '%1.0f%%')
    ax[2].pie(value_jip_pie, labels = label_vac_pie, autopct = '%1.0f%%')

    ax[0].set_title('For Infected Patients')
    ax[1].set_title('For Hospitalised Patients')
    ax[2].set_title('For ICU Patients')

    # for age_gp = ['0-24', '25-64', '65+']
    # value_poz_bar.iloc[:, [2, 1, 0]].plot.bar(ax = ax[3], stacked = True, rot = 0, color ='rcm')
    # value_hos_bar.iloc[:, [2, 1, 0]].plot.bar(ax = ax[4], stacked = True, rot = 0, color ='rcm')
    # value_jip_bar.iloc[:, [2, 1, 0]].plot.bar(ax = ax[5], stacked = True, rot = 0, color ='rcm')

    # for age_gp = ['0-14', '15-24', '25-44', '45-64', '65+']
    value_poz_bar.iloc[:, [4, 3, 2, 1, 0]].plot.bar(ax = ax[3], stacked = True, rot = 0, color ='rcmyb')
    value_hos_bar.iloc[:, [3, 2, 1, 0]].plot.bar(ax = ax[4], stacked = True, rot = 0, color ='rcmyb')
    value_jip_bar.iloc[:, [3, 2, 1, 0]].plot.bar(ax = ax[5], stacked = True, rot = 0, color ='rcmyb')

    for i, ax in enumerate(ax[3:]):
        for c in ax.containers:
            # labels = [f'{artist.get_height() / denominator[i][j] * 100  :.0f}%' for j, artist in enumerate(c)]
            ax.bar_label(c, label_type='center', labels = None) # labels = None to label with values (default), labels = labels to label with %

    fig.suptitle(f'Covid Patients Vaccination Profile Breakdown\n(aggregated value from {start_d:%Y-%b-%d} to {end_d:%Y-%b-%d})')
    return fig


if __name__ == '__main__':

    # update_vac_file() # download latest vac file (.xlsx) from website and save it to designated folder

    fig1 = plot_infect_hosp_severe_whole()
    fig2 = plot_infect_hosp_severe_parts()
    fig3 = plot_vac()

    plt.show()
