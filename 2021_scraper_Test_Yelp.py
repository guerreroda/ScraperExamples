############################
# YELP
# Last Edit: 02/15/2021
############################
# Fill bellow:
state = "TN"
# crafts:
cfts = ["Restaurants"]
# locations:
lcts = ["Knoxville"]

############################
# Libraries:
import urllib3, json; from bs4 import *
import numpy as np; import pandas as pd; import re
############################

pd.set_option('display.float_format', lambda x: '%.2f' % x)
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
urllib3.disable_warnings()
http = urllib3.PoolManager(100)

URL = "http://www.yelp.com/"
u1 = "search?"
u2 = "cflt="
u3 = "&find_loc="

def parse(url, h=http, head=hdr) :
    #parser.
    r = h.request('GET', url, headers=head).data.decode('ascii', 'ignore')
    return r

def find_biz(site, last_number=0) :
    # This function gets the data
    names = list()
    
 # if I want to introduce several cities or craft, just
# run the functions inside the loop:
for craft in cfts[0:1] :
    for loc in lcts[0:1] :
        u = URL + u1 + u2 + craft + u3 + loc.replace(" ", "+")
print(u)
s = parse(u)
last_iteration = 0

rows = []
while last_iteration >=0 :
    print("currently in bussiness number:", last_iteration)
    if last_iteration == 0 :
        data, last_iteration = find_biz(s, last_iteration)
        for i in data : rows.append(i)
    if last_iteration >0 :
        next_page=u+"&start="+str(last_iteration)
        next_page = parse(next_page)
        data, last_iteration = find_biz(next_page, last_iteration)
        for i in data : rows.append(i)
        # when to stop? when last page.
        current, final = find_pages(next_page)
        if current==final : last_iteration = -1

df = pd.DataFrame.from_dict(rows, orient='columns')
df.to_csv('Data.csv')
    all_biz = list()
    for d in BeautifulSoup(site)('div') :
        if d.get('class')!=None and "arrange__09f24__AiSIM" in d.get('class') :
            biz = dict()
            for h in d('h4') :
                if h.get('class')!=None and "heading--h4__09f24__EeWYF" in h.get('class'):
                    for a in h('a') :
                        biz['name'] = a.contents[0].strip()
                if biz['name'] not in names :
                    names.append(biz['name'])
                    for span in h('span') :
                        if str(span.contents[0]).isnumeric() :
                            biz["number"] = int(span.contents[0])
                            if biz["number"]>last_number : last_number=biz["number"]
                    if 'number' in biz :
                        for d2 in d('div') :
                            if d2.get('aria-label')!=None and "rating" in d2.get('aria-label') :
                                biz["rating"] = d2.get('aria-label')
                        for address in d('address') :
                            for span in address('span') :
                                if "raw__09f24__3Obuy" in span.get('class') :
                                    biz["address"] = span.contents[0]
                        for span in d('span') :
                            if "priceRange__09f24__2O6le" in span.get('class') :
                                biz['price_range'] = len(span.contents[0])
                        cats = list()
                        for span in d('span') :
                            if "text__09f24__1RhSS" in span.get('class') and "text-size--inherit__09f24__1CbOX"  in span.get('class') and "text-color--black-extra-light__09f24__2ZRGr" in span.get('class'):
                                for a in span('a') :
                                    if "link__09f24__1MGLa" in a.get('class') :
                                        cats.append(a.contents[0])
                        biz['categories'] = cats
                        all_biz.append(biz)
                else : break
    return all_biz, last_number

def find_pages(site) :
    # This function is necessary to iterate through pages to get all business.
    try :
        x = (re.findall(r'([0-9]*) of ([0-9]*)</span>', str(site)))[0]
        page_current = x[0]
        page_total = x[1]
    except : 
        soup = BeautifulSoup(site)
        for span in soup('span') :
            if "text-align--left__09f24__ceIWW" in span.get('class') and "text__09f24__1RhSS" in span.get('class') :
                if "of" in span.contents[0] :
                    page_current = span.contents[0].split()[0]
                    page_total = span.contents[0].split()[-1]
    return int(page_current), int(page_total)
