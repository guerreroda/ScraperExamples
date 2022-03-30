# Python 3.x
# Scraper of website Pedidos to Go
# Generates dataframe with prices and products of fastfood restaurants.

# --------------------------
# --------------------------
# PedidosToGo Scraper
# --------------------------
# --------------------------
byloc = {
    'Distrito Capital' : ["http://www.pedidostogo.com/restaurantes/caracas/altamira-16.aspx",
                         "http://www.pedidostogo.com/restaurantes/caracas/chacao-20.aspx",
                         "http://www.pedidostogo.com/restaurantes/caracas/chacaito-33.aspx",
                         "http://www.pedidostogo.com/restaurantes/caracas/las-mercedes-13.aspx",
                         "http://www.pedidostogo.com/restaurantes/caracas/baruta-119.aspx",
                         "http://www.pedidostogo.com/restaurantes/caracas/el-hatillo-155.aspx",
                         "http://www.pedidostogo.com/restaurantes/caracas/colinas-de-bello-monte-35.aspx",
                         "http://www.pedidostogo.com/restaurantes/caracas/los-naranjos-222.aspx",
                         "http://www.pedidostogo.com/restaurantes/caracas/la-boyera-178.aspx",
                         "http://www.pedidostogo.com/restaurantes/caracas/la-trinidad-190.aspx"]
    }
rows = list()
f_time = time.time()
for state, urls in byloc.items() :
    done = list()
    for url in urls :
        s_time = time.time()
        response = http.request('GET', url, headers=hdr).data   
        print('Connected:', url.split("/")[-1].replace(".aspx", "")[:-3].replace("-", " ").strip(), state)
        soup = BeautifulSoup(response)
        for li in soup('li') :
            if li.get('class')!=None and "title-manufacturer" in li.get('class') :
                for a in li('a') : 
                    seller = a.contents[0]
                    if seller in done : continue
                    else :
                        s = BeautifulSoup(http.request('GET', a.get('href'), headers=hdr).data)
                        for l in s('li') :
                            if l.get('class')!=None and "box-rating" in l.get('class') :
                                for star in l('img') :
                                    try :
                                        st = ""
                                        for k in star.get('title') :
                                            st = st + k
                                        stars = float(st.replace(",", "."))
                                        break
                                    except : continue
                            else : continue
                        for t in s('table') :
                            if t.get('class')!=None and "res-product-item" in t.get('class') :
                                data = dict()
                                tds = t('td')
                                for td in tds :
                                    if td.get('class')!= None and "res-cl1" and td.get('class') :
                                        for a in td('a') :
                                            if a.get('class')!=None and "product-title" in a.get('class') :
                                                data['item-name'] = a.contents[0].strip()
                                                data['id-item']= a.get('href').replace(".aspx", "").split("/")[-1]
                                    if td.get('class')!=None and 'res-cl2' in td.get('class') : 
                                        for sp in td('span') :
                                            if float(sp.contents[0].replace("Bs.S","").replace("Bs","").replace("Bs.F.","").strip()[:-3].replace(".","")) == 0 :
                                                data['price'] = np.nan
                                            else : data['price'] = float(sp.contents[0].replace("Bs.S","").replace("Bs","").replace("Bs.F.","").strip()[:-3].replace(".",""))
                                data['cat_0'] = 'restaurants'
                                data['subcategory'] = seller
                                data['location'] = url.split("/")[-2]
                                data['urb'] = url.split("/")[-1].replace(".aspx", "")[:-3].replace("-", " ").strip()
                                data['reputation'] = stars
                                data['state'] = state
                                data['date_scraped'] = time.strftime("%Y-%m-%d")
                                rows.append(data)
                        done.append(seller)
        print('Scraped.', str(time.time()-s_time))
new_ptogo = pd.DataFrame.from_dict(rows, orient='columns')
new_ptogo['date_scraped']= pd.to_datetime(new_ptogo['date_scraped'], format='%Y-%m-%d')
new_ptogo = new_ptogo.set_index(['date_scraped', 'id-item'])
print('saving...')

with open(cdir+'data_ptogo.json') as data_file: data = json.load(data_file)
df_togo = pd.DataFrame(data)
df_togo['date_scraped']= pd.to_datetime(df_togo['date_scraped'], unit='ms')
df_togo = df_togo.set_index(['date_scraped', 'id-item'])
df_togo = df_togo.sort_index()
df_togo = pd.concat([df_togo[~df_togo.index.isin(new_ptogo.index)], new_ptogo])
del new_ptogo
'''
with open(cdir+'data_ptogo.json', "w") as output_file:
    output_file.write(df_togo.reset_index().to_json())
    output_file.close()

print('df_togo saved, loaded and updated')
'''
print('Total time:', str((time.time()-f_time)/60), "m.")
#df_togo = df_togo.reset_index()
