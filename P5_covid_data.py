import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
from urllib.request import urlopen

# source data
json_hosp = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/hospitalizace.json"
json_infect = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakazeni-vyleceni-umrti-testy.json"


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

# pd.set_option('display.max_rows', None)
# print(df_hosp_ratio)
# print(df_severe_ratio)


x = df_date_infect
y1 = df_infect
y2 = df_hosp
y3 = df_severe
y4 = df_hosp_ratio
y5 = df_severe_ratio
ylabel = 'no. of patients'


fig, ax = plt.subplots(nrows=2, ncols=1, figsize = (15, 8))

ax[0].plot(x, y1, 'y', label = "infected")
ax[0].plot(x, y2, 'b', label = "hospitalised")
ax[0].plot(x, y3, 'r', label = "severe/ICU")
ax[1].plot(x, y4, 'b.', label = "ratio of hospitalised over infected")
ax[1].plot(x, y5, 'r.', label = "ratio of severe/ICU over hospitalised")

for ax0 in ax:
    ax0.set(xlabel='date')
    ax0.legend()

ax[0].set(title="Covid Situation in Czech Republic", ylabel='no. of patients')
ax[1].set(ylabel='ratio')

plt.show()
