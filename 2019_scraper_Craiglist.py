# Python 3.x
# Scrapes Craiglist
# No idea the purose of this program as it was done several years ago.

import re, urllib3, json, time
from bs4 import BeautifulSoup
import pandas as pd
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
http = urllib3.PoolManager(10)
urllib3.disable_warnings()
import datetime
now = datetime.datetime.now()

list_city = ['chicago', 'newyork', 'losangeles', 'houston', 'philadelphia']
list_sale = {
    'cell_phones' : 'moa',
    'antiques' : 'ata',
    'appliances' : 'ppa',
    'arts_crafts' : 'ppa',
    'atv' : 'sna',
    'auto_parts' : 'pta',
    'baby, kid' : 'baa',
    'beauty, health' : 'haa',
    'bikes' : 'bia',
    'boats' : 'boo',
    'boat parts' : 'bpa',
    'books' : 'bka',
    'cars' : 'cta',
    'clothes' : 'cla',
    'computer parts' : 'syp',
    'computers' : 'sya',
    'free' : 'zip',
    'furniture' : 'fua',
    'household' : 'hsa',
    'jewelry' : 'jwa',
    'music instrument' : 'msa',
    'toys' : 'taa',
    'videogames' : 'vga'
}

u_posted = 'postedToday=1'
u_pic = 'hasPic=1'
u_cl = '.craigslist.org/search/'

rows  = []
for c in list_city :
    print('scraping', c)
    for k, s in list_sale.items() :
        link = "https://" + c + u_cl + s + "?" + u_posted + "&" + u_pic
        response = http.request('GET', link, headers=hdr)
        site = response.data
        l = re.findall(r'<span class="rangeTo">([\d]*)<\/span>', str(site))
        try : count = l[0]
        except : count = 0
        data = {
            'city' : c,
            'category' : k,
            'category_code' : s,
            'totalcount' : count,
            'date' : now.strftime("%Y-%m-%d"),
        }
        rows.append(data)
print('End.')

df = pd.DataFrame.from_dict(rows, orient='columns')
df = df.set_index(['date', 'category_code'])
#del df['index']
cdir = "C:/"

with open(cdir+'data_craiglist.json') as data_file: data = json.load(data_file)
df_or = pd.DataFrame(data)
df_or = df_or.set_index(['date', 'category_code'])
df = pd.concat([df_or[~df_or.index.isin(df.index)], df])
