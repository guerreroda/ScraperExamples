# Python 2.7
# Last Edit: 2019
# Diego A. Guerrero

import re, urllib3, json, time
from bs4 import BeautifulSoup
import unicodedata, string
import pandas as pd
pd.set_option('display.float_format', lambda x: '%.2f' % x)
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
http = urllib3.PoolManager(100)
urllib3.disable_warnings()

# mercado libre is in Spanish. Scrapping requires reading Spanish characters
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

# examine available data.
with open('data/data_lm.json') as data_file: data = json.load(data_file)
data_pricelm = pd.DataFrame(data)
data_pricelm['date_scrapped'] = pd.to_datetime(data_pricelm['date_scrapped'], unit='ms')
data_pricelm = data_pricelm.set_index(['date_scrapped', 'id-item'])

from random import randint

def ML_explorer(site) :
    pages = [0]
    soup = BeautifulSoup(site)
    # Extract All Pages
    div_full = soup('div')
    for div in div_full :
        if div.get('class') == 'pagination__container' :
            a_tags = div('a')
            for a in a_tags :
                if len(a.get('href')) > 4 : pages.append(a.get('href'))
        else : continue
    
    # Iterate Through each Page
    item_links = list()
    pages_soups = list()
    for s in pages :
        if s != 0 :
            response = http.request('GET', s, headers=hdr)
            soup_page = BeautifulSoup(response.data)
        elif s==0 : soup_page = soup
        pages_soups.append(soup_page)
    
    # Extract Item Links
    for soup_page in pages_soups :
        li_tags = soup_page("li")
        for li in li_tags :
            if isinstance(li.get('class'), str) or isinstance(li.get('class'), unicode) : 
                if li.get('class').startswith("results-item article") :
                    a_tags = li('a')
                    for a in a_tags :
                        if isinstance(a.get('class'), str) or isinstance(a.get('class'), unicode) :
                            if a.get('class').startswith("item__info-link") : item_links.append(a.get('href'))
                            else : continue
                        else : continue
                else : continue
            else : continue
    #print item_links[0:2]                  # Limit Here for test purposes.
    return item_links

def item_explorer(links, subcategory, start, pause_con=False) :
    cont = ""
    items_data = []
    c = 0
    items_sites = []
    print 'Retrieving items...'
    for l in links :
        try :
            response = http.request('GET', l, headers=hdr)
            item_site = response.data
        except :
            d = randint(3,60*3)
            print 'random delay', float(d/60), "m."
            time.sleep(d)
            response = http.request('GET', l, headers=hdr)
            item_site = response.data
        c = c+1
        if c == int(len(links)*1/4) or c == int(len(links)*1/3) or c == int(len(links)*1/2) or c == int(len(links)*3/4) or  c == int(len(links)*8/9) :
            print subcategory + ": ", c, " of ", len(links)
        items_sites.append(item_site)
        import time
        t = time.time() - start
        if t>=(30*60) and pause_con==True :
            print 'Execution time:', t/60, "mins"
            print 'Items scrapped:', len(items_sites)
            cont = raw_input('continue? y/n: ').strip().lower()[0]
        else : start, cont = time.time(), 'y'
        if cont.lower() == 'n' or cont.lower() == "no" : break
    
    print subcategory, 'items retrieved. scrapping...'
    for item_site in items_sites :
        item_soup = BeautifulSoup(item_site)
        item = { 'subcat' : subcategory }
        all_span = item_soup('span')
        # Retrieve item ID
        for sp in all_span :
            if sp.get('class') == "id-item" : item['id-item'] = sp.contents[0].split()[1].replace("#","")
            elif sp.get('class') == "where" :
                contenido = sp.contents[0].split(",")
                if len(contenido)>1 :
                    item['location'] = contenido[0]
                    item['state'] = contenido[1]
                elif len(contenido) == 1 :
                    if len(contenido[0].split("(")) > 1 :
                        item['location'] = contenido[0].split("(")[0]
                        item['state'] = contenido[0].split("(")[1].replace(")","")
                    else : item['location'] = sp.contents[0]
                else : item['location'] = sp.contents[0]
            elif sp.get('data-block') == "installmentsQuantity" : item['Quantity'] = sp.contents[0]
        if 'id-item' not in item : 
            for link in item_soup('link') :
                if link.get('rel')=="canonical" : item['id-item'] = link.get('href').split("/")[-1:][0].split("-")[1]
        if 'location' not in item and 'state' not in item :
            for p in item_soup('p') :
                if p.get('class') == "custom-address" :
                    item['location'] = p.contents[0].contents[0].strip().split(",")[0].strip()
                    item['state'] = p.contents[0].contents[0].strip().split(",")[1].strip()
        all_ul = item_soup('ul')
        for ul in all_ul :
            if ul.get('class') == "vip-navigation-breadcrumb-list" :
                list_as = ul('a')
                for a in list_as :
                    item["cat_"+str(list_as.index(a))] = remove_accents(a.contents[0]).translate(string.maketrans("\n\t\r", "   "))
        # Price
        article_tags = item_soup('article')
        for article in article_tags :
            if article.get('class') == "vip-price ch-price" :
                for t in article('strong') :
                    if len(t.contents[0].split())>0:
                        price=float(t.contents[0].split()[1].replace(".",""))
                    else : price = t.contents[0]
                for t in article('sup') :
                    if len(t.contents[0])>0 : price_decimal=float(t.contents[0])/100
                if price<1000 :
                    price = price*1000
                    item['alert'] = "price"
                else : item['alert'] = None
                item['price'] = price + price_decimal
            else : continue
        if 'price' not in item :
            for f in item_soup('fieldset') :
                if f.get('class').startswith('item-price') :
                    for sn in f('span') :
                        if sn.get('class') == "price-tag-fraction" :
                            item['price'] = float(sn.contents[0].split()[0].replace(".",""))
                elif f.get('class').startswith('vip-price') :
                    for article in f('article') :
                        if article.get('class').startswith("vip-price") :
                            for t in article('strong') :
                                item['price'] = float(t.contents[0].split()[1].replace(".",""))
                        else : continue
                else : continue
        # Product Name
        h1_tags = item_soup('h1')
        for h1 in h1_tags :
            if h1.get('class') == "vip-title-main " or h1.get('class') == "item-title__primary" : item['item-name'] = h1.contents[0]
            else : continue
        # Reputation Elements
        dd_tags = item_soup('dd')
        for dd in dd_tags :
            if dd.get('class') == 'reputation-relevant' :
                    spans = dd('span')
                    for span in spans :
                        if span.get('class') == "reputation-data-sales" :
                            for i in dd('strong') : item['sales'] = i.contents[0]
                        else :
                            for i in dd('strong') : item['reputation'] = i.contents[0]
        item['date_scrapped'] = time.strftime("%Y-%m-%d")
        items_data.append(item)
    return items_data, cont.lower()

# Main scrapper:
def scrapper_ml(formato) :
    if formato == 'tiendas' : url_mercado = "http://www.mercadolibre.com.ve/tiendas-oficiales"
    elif formato == 'ventas' : url_mercado = "https://www.mercadolibre.com.ve/jm/ml.allcategs.AllCategsServlet"
    else :
        print 'error formato. tiendas/ventas'
        return
    if formato=='ventas' and 'data_ml' in locals() : backup = data_ml
    elif formato=='tiendas' and 'data_ml_tiendas' in locals() : backup = data_ml_tiendas
    connection_pause = raw_input('Request stop after 30mins? True/False: ').strip().lower()[0]
    response = http.request('GET', url_mercado, headers=hdr)
    ml_site = response.data
    soup = BeautifulSoup(ml_site)
    
    ml_cats = []
    if formato == "tiendas" :
        for section in soup('section') :
            if section.get('class') == "brands-wrapper container" :
                for a in section('a') :
                    if a.get('class').startswith('lazy-image') : ml_cats.append([a.get('href'), remove_accents(a.get('data-alt'))])
        print 'tiendas loaded'
    elif formato == 'ventas' :
        for a in soup('a') :
            if a.get('class') =="seglnk" : ml_cats.append([a.get('href'), remove_accents(a.contents[0])])
        print 'Subcategories loaded'
    data_ml_rows = []
    
    # Enter site
    count_cats = 0
    continuation = ""
    for sub_page in ml_cats :
        if continuation == "n" or continuation=="no" : break
        start_time = time.time()
        url_ML = sub_page[0]
        subcat = sub_page[1]
        if 'backup' in locals() :
            if any(backup['subcat']==subcat)==True : ignore = True
        else : ignore = False
        
        # Connect to categories
        if ignore==False :
            response = http.request('GET', url_ML, headers=hdr)
            ml_site = response.data
            print 'Connected to:', subcat
            if connection_pause == "t" :
                items, continuation = item_explorer(ML_explorer(ml_site), subcat, start_time, pause_con=True)
            else : items, continuation = item_explorer(ML_explorer(ml_site), subcat, start_time)
            for d in items : data_ml_rows.append(d)
            count_cats = count_cats+1
            print subcat, 'scrapped. Continue...'
            if count_cats == int(len(ml_cats)*1/4) or count_cats == int(len(ml_cats)*1/3) or count_cats == int(len(ml_cats)*1/2) or count_cats == int(len(ml_cats)*3/4) or  count_cats == int(len(ml_cats)*8/9) :
                print "Category: ", count_cats, " de ", len(ml_cats)
        elif ignore == True :
            count_cats = count_cats+1
            print 'subcategory already in backup.'
    data = pd.DataFrame.from_dict(data_ml_rows, orient='columns')
    data = data.set_index(['date_scrapped', 'id-item'])
    if 'backup' in locals() :
        data = pd.concat([data[~data.index.isin(backup.index)], backup])
        del backup
    return data


print 'Scrapping functions loaded'

# Update data ventas
if raw_input('Begin scrapping MercadoLibre? y/n: ').strip().lower()[0] == "y" :
    data_ml_tiendas = scrapper_ml('ventas')
else : print 'Not scrapped.'# Update data tiendas

if raw_input('Begin scrapping Tiendas ML? y/n: ').strip().lower()[0] == "y" :
    data_ml_tiendas = scrapper_ml('tiendas')
else : print 'Not scrapped.'
