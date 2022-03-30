# Python 3.x
# Last Edit: 2019
# Parses LicoresMundiales.com.ve
# Generates json data file with price and characteristics of products.

import re, urllib3, json, time
from bs4 import BeautifulSoup
import unicodedata, string
import pandas as pd
import numpy as np
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
http = urllib3.PoolManager(100)
urllib3.disable_warnings()
%matplotlib inline

cdir = 

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii
from random import randint

# --------------------------
# --------------------------
# lm Scraper (10/20/2019)
# --------------------------
# --------------------------

def parse_pages(web) :
    soup = BeautifulSoup(web)
    links = list()
    for a in soup('a') :
        if a.get('class')!=None and "page" in a.get('class') : links.append(a.get('href'))
    return links

def find_items(web, cat, data=list()) :
    soup = BeautifulSoup(web)
    for d in soup('div') :
        if d.get('class')!=None and 'product-item-details' in d.get('class') :
            item = { 'category' : 'bebidas alcoholicas',
                    'subcategory' : cat[0]}
            # FIND NAME AND ID OF ITEM
            for a in d('a') :
                if a.get('class')!=None and 'product-item-link' in a.get('class') :
                    item['id-item'] = a.get('href')[:-1].split("/")[-1].replace(".htm","")
                    item['item-name'] = str(a.get('href')[:-1].split("/")[-1].replace(".htm","").replace("-"," "))
            # FIND PRICES VECTOR
            prices = dict()
            for li in d('li') :
                if li.get('class')!=None and 'tier-item' in li.get('class') :
                    for span in li('span') :
                        if span.get('class')!=None and "units" in span.get('class') :
                            unt = int(str(span.contents[0]).lower().replace("+"," ").lstrip().rstrip().replace("unds","").replace("und",""))
                        elif span.get('class')!=None and "price" in span.get('class') :
                            price = float(span.contents[0].replace("Bs.","").replace(".",""))
                    prices[unt] = price
            # FIND CHARACTERISTICS
            for di in d('div') :
                if di.get('class')!=None and 'value' in di.get('class') :
                    values = list()
                    for s in di('span') :
                        if "lts" in s.contents[0].lower() : item['size'] = s.contents[0]
                        elif "sin" in s.contents[0].lower() : item['year'] = s.contents[0]
                        elif s.contents[0].strip().isdigit() : item['year'] = s.contents[0]
                        else : item['country'] = s.contents[0]
            item['date_scraped'] = time.strftime("%Y-%m-%d")
            item["price"] = prices[min(prices.keys())]
            item["units"] = min(prices.keys())
            del prices, values
            data.append(item)
    return data


full_t = time.time()
start_time = time.time()
licores_url1 = "https://www.licoresmundiales.com/"
print("Scraping Licores Mundiales...")
site = http.request('GET', licores_url1, headers=hdr).data
soup = BeautifulSoup(site)
categorias = []
for l in soup('a') :
    if l.get('class') != None and 'level-top' in l.get('class') :
        categorias.append([str(l.contents[0]).replace("<span>","").replace("</span>",""), l.get('href')])
print('Links retrieved')
limit = '?product_list_limit=200'

item_list = []
for c in categorias :
    print('scraping', c[0])
    url_c = c[1] + limit
    response = http.request('GET', url_c, headers=hdr)
    print('connected.')
    find_items(response.data, c, item_list)
    cnt = 1
    for p in parse_pages(response.data) :
        # PARSE THROUGH OTHER PAGES
        cnt = cnt+1
        print('page:', cnt)
        find_items(http.request('GET', p, headers=hdr).data, c, item_list)
print('Scraped.', (time.time()-start_time)/60, "m.")

df_newlm = pd.DataFrame.from_dict(item_list, orient='columns')
df_newlm['date_scraped'] = pd.to_datetime(df_newlm['date_scraped'], format='%Y-%m-%d')
df_newlm = df_newlm.set_index(['date_scraped', 'id-item'])
print('saving...')
with open(cdir+'data_lm.json') as data_file: data = json.load(data_file)
df_lm = pd.DataFrame(data)
df_lm['date_scraped'] = pd.to_datetime(df_lm['date_scraped'], unit='ms')
df_lm = df_lm.set_index(['date_scraped', 'id-item'])
df_lm = pd.concat([df_lm[~df_lm.index.isin(df_newlm.index)], df_newlm])
del df_newlm
#del df_lm['index'], df_lm['cat_1']
with open(cdir+'data_lm.json', "w") as output_file:
    output_file.write(df_lm.reset_index().to_json())
    output_file.close()
print('df_lm saved, loaded and updated')
