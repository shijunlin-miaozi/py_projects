import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import json
import os
import time
import webbrowser
from urllib.request import urlopen
from datetime import datetime, timedelta, date

# pd.set_option('display.max_rows', None) # to display all rows of data in a dataframe

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
d_infect.index = d_hosp.index

df_date, df_hosp, df_severe = pd.to_datetime(d_hosp['datum']), d_hosp["pocet_hosp"], d_hosp["stav_tezky"]
df_infect, df_infect_new = d_infect["kumulativni_pocet_nakazenych"] - d_infect["kumulativni_pocet_vylecenych"] - d_infect["kumulativni_pocet_umrti"], d_infect["prirustkovy_pocet_nakazenych"]

df_overview = pd.concat([df_date, df_infect, df_infect_new, df_hosp, df_severe, (df_hosp / df_infect), (df_severe / df_hosp)], axis=1)
df_overview.columns = ["date", "total infected", "newly infected", "hospitalised", "severe/ICU", "ratio of hospitalised over total infected", "ratio of severe/ICU over hospitalised"]

df_vac = pd.read_excel(path_vac, sheet_name = None)
df_poz, df_hos, df_jip = df_vac['pozitivity'], df_vac['hospitalizace'], df_vac['jip']


def clean_vac_data(cutoff, df, age_gp): # cutoff format: [(y, m, d), (y, m, d)], age_gp = 3 or 5
    df = df[(df['od'].dt.date >= date(*cutoff[0])) & (df['od'].dt.date <= date(*cutoff[1]) - timedelta(days=6))]
    start_d, end_d = df['od'].min(), df['od'].max() + timedelta(days=6)
    df = df.assign(age = df['vek_kategorie'].apply(lambda x: x.split('-')[0] if len(x.split('-')[0]) < 2 else x.split('-')[0][:2]).values)
    
    if age_gp == 3: # for age_gp = ['0-24', '25-64', '65+']
        df = df.assign(age_gp = df['age'].apply(lambda x: 'unknown' if x == 'ne' else '0-24' if int(x) < 25 else '65+' if int(x) > 64 else '25-64').values)
    elif age_gp == 5: # for age_gp = ['0-14', '15-24', '25-44', '45-64', '65+']
        df = df.assign(age_gp = df['age'].apply(lambda x: 'unknown' if x == 'ne' else '0-14' if int(x) < 15 else '65+' if int(x) > 64 else '15-24' if int(x) < 25 else '25-44' if int(x) < 45 else '45-64').values)
    else:
        print("Only 2 types of age_gps available: 3 for ['0-24', '25-64', '65+'] and 5 for ['0-14', '15-24', '25-44', '45-64', '65+']")
        return
    df_bydate = df.groupby('od').sum().sum()
    df_byage = df.groupby('age_gp').sum().iloc[:age_gp] # rows of unknown age are removed (16 out of 50,000 for df_poz total infected)
    df_byage = df_byage.assign(w_vac = (df_byage.iloc[:, 0] - df_byage.iloc[:, 1]).values)
    value_pie = df_bydate.iloc[1], df_bydate.iloc[2], df_bydate.iloc[3], df_bydate.iloc[4]
    value_bar = df_byage.iloc[::-1, [0, 1, -1]].transpose()
    return value_pie, value_bar, start_d, end_d


def plot_overview():
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (14, 7))

    for n, col, style in zip([0]*4 + [1]*2, range(1, 7), ('y', 'y:', 'b', 'r', 'b.', 'r.')):
        ax[n].plot(df_overview['date'], df_overview.iloc[:, col], style, label = df_overview.columns[col])

    for ax0 in ax:
        ax0.set(xlabel='date')
        ax0.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b-%d'))
        ax0.grid()
        ax0.legend()
    ax[0].set(ylabel='no. of patients', title=f'Covid Situation in Czech Republic from {df_date.min(): %Y-%b-%d} to {df_date.max(): %Y-%b-%d})')
    ax[1].set(ylabel='ratio')
    fig.autofmt_xdate()
    return fig


def plot_ratio_periods(p1, p2, duration=90): # p1 & p2 are end dates of periods to be shown; format: (y, m, d)
    df1 = df_overview[(df_overview['date'].dt.date > date(*p1) - timedelta(days=duration)) & (df_overview['date'].dt.date <= date(*p1))]
    df2 = df_overview[(df_overview['date'].dt.date > date(*p2) - timedelta(days=duration)) & (df_overview['date'].dt.date <= date(*p2))]
    ylim_infect_max = (max(df1.iloc[:, 1].max(), df2.iloc[:, 1].max()) * -1 // 500) * -500
    ylim_ratio_max = (max(df1.iloc[:, -1].max(), df2.iloc[:, -1].max()) * -1 // 0.05) * -0.05

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize = (14, 7))

    ax = ax.flatten()
    for n, col, style in zip([0]*4 + [2]*2, range(1, 7), ('y', 'y:', 'b', 'r', 'b.', 'r.')):
        ax[n].plot(df1['date'], df1.iloc[:, col], style, label = df1.columns[col])

    for n, col, style in zip([1]*4 + [3]*2, range(1, 7), ('y', 'y:', 'b', 'r', 'bx', 'rx')):
        ax[n].plot(df2['date'], df2.iloc[:, col], style, label = df2.columns[col])

    for ax0 in ax:
        ax0.set(xlabel='date')
        ax0.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b-%d'))
        ax0.grid()
        ax0.legend()
    ax[0].set(xlim=[df1['date'].min(), df1['date'].max()], ylim=[0,ylim_infect_max], ylabel='no of patients', title=f"{duration} days data from {df1['date'].min(): %Y-%b-%d} to {df1['date'].max(): %Y-%b-%d}")
    ax[1].set(xlim=[df2['date'].min(), df2['date'].max()], ylim=[0,ylim_infect_max], ylabel='no of patients', title=f"{duration} days data from {df2['date'].min(): %Y-%b-%d} to {df2['date'].max(): %Y-%b-%d}")
    ax[2].set(xlim=[df1['date'].min(), df1['date'].max()], ylim=[0,ylim_ratio_max], ylabel='ratio')
    ax[3].set(xlim=[df2['date'].min(), df2['date'].max()], ylim=[0,ylim_ratio_max], ylabel='ratio')
    fig.autofmt_xdate()
    return fig


def plot_vac(cutoff, age_gp=3, bar_label_style='value'): # cutoff format: [(y, m, d), (y, m, d)] both dates inclusive, age_gp = 3 or 5, bar_label_style = 'value' or '%'
    label_vac_pie = ['Without Vac', 'With 1 Shot', 'With 2 Shots', 'With Booster']
    label_vac_bar = ['Total', 'Without Vac', 'With Vac']
    value_poz_pie, value_poz_bar, start_d, end_d = clean_vac_data(cutoff, df_poz, age_gp)
    value_hos_pie, value_hos_bar, _, _ = clean_vac_data(cutoff, df_hos, age_gp)
    value_jip_pie, value_jip_bar, _, _ = clean_vac_data(cutoff, df_jip, age_gp)
    for df in (value_poz_bar, value_hos_bar, value_jip_bar):
        df.index = label_vac_bar
    denominator = [[sum(val), val[0], sum(val) - val[0]] for val in (value_poz_pie, value_hos_pie, value_jip_pie)]

    fig, ax = plt.subplots(nrows=2, ncols=3, figsize = (14, 7))
    
    ax = ax.flatten()
    for n, value in zip(range(3), (value_poz_pie, value_hos_pie, value_jip_pie)):
        ax[n].pie(value, labels = label_vac_pie, autopct = '%1.0f%%')
    
    for n, title in zip(range(3), ('For Infected Patients', 'For Hospitalised Patients', 'For ICU Patients')):
        ax[n].set_title(title)

    if age_gp == 3: # for age_gp = ['0-24', '25-64', '65+']
        for value, n in zip((value_poz_bar, value_hos_bar, value_jip_bar), range(3, 6)):
            value.plot.bar(ax = ax[n], stacked = True, rot = 0, color ='rcm')

    if age_gp == 5: # for age_gp = ['0-14', '15-24', '25-44', '45-64', '65+']
        for value, n in zip((value_poz_bar, value_hos_bar, value_jip_bar), range(3, 6)):
            value.plot.bar(ax = ax[n], stacked = True, rot = 0, color ='rcmyb')

    for i, ax in enumerate(ax[3:]):
        for c in ax.containers:
            if bar_label_style == '%':
                labels = [f'{artist.get_height() / denominator[i][j] * 100  :.0f}%' for j, artist in enumerate(c)]
                ax.bar_label(c, label_type='center', labels = labels) # labels = labels to label with %
            else:
                ax.bar_label(c, label_type='center') # labels = None to label with values (default)

    fig.suptitle(f'Covid Patients Vaccination Profile Breakdown\n(aggregated value from {start_d:%Y-%b-%d} to {end_d:%Y-%b-%d})')
    return fig


if __name__ == '__main__':

    update_vac_file() # # download latest vac file (.xlsx) from website and save it to designated folder

    fig1 = plot_overview()
    fig2 = plot_ratio_periods((2021, 3, 10), (2021, 11, 15))
    wave4 = plot_vac(cutoff=[(2021, 9, 1), (2021, 10, 24)], age_gp=5, bar_label_style='%')
    wave3 = plot_vac(cutoff=[(2021, 2, 1), (2021, 6, 1)], age_gp=5, bar_label_style='%')
    wave2 = plot_vac(cutoff=[(2021, 1, 1), (2021, 1, 31)], age_gp=5, bar_label_style='%')

    plt.show()