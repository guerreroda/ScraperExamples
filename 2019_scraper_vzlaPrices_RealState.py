# Last Edit: 2018-2019
# Python 2.x
# Scraper of El Universal, news website.
# Finds prices and characteristics of properties advertised and sold in Venezuela.

import unicodedata, string, time
import numpy as np; import pandas as pd

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

import urllib3, json; from BeautifulSoup import *
pd.set_option('display.float_format', lambda x: '%.2f' % x)
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
urllib3.disable_warnings()
http = urllib3.PoolManager(100)
main_url = "https://clasificadoseluniversal.com"
rows = list()
full_done = list()
main = "https://clasificadoseluniversal.com/buscar/INMUEBLE.action?transaccion="
cat = "&categoria="
page = "&pagina="
tra = ["VENTA", "ALQUILER"]

address_file = "C:/Users/Diego/Dropbox (Personal)/my-notebook/data_track/data/data_restate.json"

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

def euitem_extract(item_url, h=hdr, ht=http) :
    data = dict()
    r = ht.request('GET', item_url, headers=h).data
    soup = BeautifulSoup(r)
    for h in soup('h2') :
        for i in h('i') :
            if str(i.contents[0].replace(".","")).isdigit()==False or int(i.contents[0].replace(".",""))==0 : price = np.nan
            else :
                if float(i.contents[0].replace(".","")) == 1 : price = np.nan; data['flag_price'] = "1"
                else : price = float(i.contents[0].replace(".",""))
    try : data['price'] = price
    except : data['price'] = np.nan
    for p in soup('p') :
        if p.get('align')!=None and p.get('align') == 'justify' and p.get('class')!=None and p.get('class')=='InfoC clear' :
            data['description'] = str(remove_accents(p.contents[0])).replace('"','')
    for div in soup('div') :
        if div.get('class') == "InfoC clear" :
            location = str(div.contents[0])[4:-5].replace("&nbsp;","").replace("Venezuela - ","")
        if div.get('class') == "CleanAll" :
            for b in div('b') : data['cat_2'] = b.contents[0]
    try : data['location'] = location.replace(" -", ",")
    except : data['location'] = np.nan
    for h in soup('h1') : 
        if h.get('style')!=None and h.get('style')=='clear:both;' :
            data['item-name'] = h.contents[0]
            data['cat_0'] = 'real estate'
            data['cat_1'] = h.contents[0].split(",")[-1]
    for li in soup('li') : 
        if li.get('class')!=None and li.get('class').startswith("Clearfix") :
            for b in li('b') : k = remove_accents(b.contents[0])
            for em in li('em') :
                if  em.contents[0] == "Si" : v = 1
                elif em.contents[0] == "No" : v = 0
                elif str(em.contents[0]).isdigit() : v = int(em.contents[0])
            try : data[k]=v
            except : data[k]=np.nan
    data['date_scraped'] = time.strftime("%Y-%m-%d"); data['id-item'] = str((main_url+a.get('href')).split("-")[-1])
    data['item_url'] = item_url
    return data
print 'Loaded'
