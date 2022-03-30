# Python 2.x
# This program used private data from political parties
# Finds the voting locations determined by electoral authorities to each individuals
# The purpose was to locate if participants in political programs had the ability to vote.

#VERSION 2.2
import urllib
from BeautifulSoup import *
import time
import csv
from itertools import islice
start_time = time.time()

url = "http://www.cne.gob.ve/web/registro_electoral/firmantes.php?nacionalidad=V&cedula="

CI = list()
n = 0

#LECTOR DE CEDULAS A BUSCAR
csvfile = open('.csv', 'rb')
#ESTABLECER UN RANGO DE BUSQUEDA
rang = list()
while len(rang) != 2 :
    for a in raw_input("Insertar rango. Ejemplo: 1 1500: >").split() :
        if a == "total" : a = 1678541
        rang.append(int(a))

#HACER LISTA DE CEDULAS EN RANGO
for row in islice(csvfile,rang[0],rang[1]) :
        l = row.split()[0]
        #print l, type(l)
        #cen = line.split("-")[1]
        CI.append(l)
print 'Total individuos a buscar:', len(CI)

#NOMBRE DE ARCHIVO CSV.
name = "validar_" + str(rang[0]) + "-" + str(rang[1]) + ".csv"


#CI = [19209745, 4086021, 19532573]
#name = "validar.csv"
#LOG DE ERRORES
log = open("log.txt", 'w')
log.write('Conexiones fallidas:\n')

count = 0
#CREAR ARCHIVO
with open(name, 'wb') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    header = ["cedula", "elector", "validar", "estado", "municipio", "parroquia", "centro", "direccion"]
    wr.writerow(header)
    print 'Comenzando busqueda...'
    #BUSCAR CADA CEDULA
    fallos = 0
    for i in CI :
        Validar = 0
        time_perci = time.time()
        #BUSCAR EN EL REP SI ES UN ELECTOR VALIDO.
        rep = "http://www.cne.gob.ve/web/registro_electoral/ce.php?nacionalidad=V&cedula=" + str(i)
	conex = False
	while conex == False :
	    try :
                s = urllib.urlopen(rep).read()
		conex = True
	    except :
                #ERROR DE CONEXION
	        conex = False
		print 'Error de conexion 1. Guardados:', count
		fallos = fallos + 1
		if fallos == 30 :
		    fallos = 0
		    log.write('CI: ' + str(i) + '\n')
		    continue
		elif fallos % 10 == 0 :
		    print 'Esperando 10 minutos...'
		    wait1 = time.time()
		    wait2 = time.time()
		    wait = (wait2 - wait1)/60
		    while wait < 10 :
		        wait2 = time.time()
			wait = (wait2 - wait1)/60
		    print 'Continuando...'
        soup = BeautifulSoup(s)
        Elector = 1
        fonts = soup('font')
        for fon in fonts :
            if fon.get('color') == "#ff0000" :
                #ELECTOR INVALIDO
                estado = "NA"
                municipio = "NA"
                parroquia = "NA"
                centro = "NA"
                direccion = "NA"
                Elector = 0
                Validar = 0
        if Elector == 1 :
            #PARA ELECTOR VALIDO.
            tables = soup('table')
            for table in tables :
                trs = table('tr')
                for tr in trs :
                    tds = tr('td')
                    for td in tds :
                        if td.get('align') == "left" :
                            font = td('font')
                            for f in font :
                                #BUSCAR SU AREA Y CENTRO DE VOTACION
                                if str(f.contents[0]) == "Estado:" : estado = tds[tds.index(td) + 1].contents[0]
                                if str(f.contents[0]) == "Municipio:" : municipio = tds[tds.index(td) + 1].contents[0]
                                if str(f.contents[0]) == "Parroquia:" : parroquia = tds[tds.index(td) + 1].contents[0]
                                if str(f.contents[0]) == "Centro:" :
                                    for n in tds[tds.index(td) + 1]('font') : centro = n.contents[0]
                                if str(f.contents[0]).startswith("Direcci") :
                                    for n in tds[tds.index(td) + 1]('font') : direccion = n.contents[0]
            #BUSCAR SI DEBE VALIDAR FIRMA.
            u = url + str(i)
	    conex = False
	    while conex == False :
	        try :
                    s = urllib.urlopen(u).read()
		    conex = True
	        except :
                    #ERROR DE CONEXION
	            conex = False
		    print 'Error de conexion 2. Guardados:', count
		    fallos = fallos + 1
		    if fallos == 30 :
		        fallos = 0
		        log.write('CI: ' + str(i) + '\n')
		        continue
		    elif fallos % 10 == 0 :
		        print 'Esperando 10 minutos...'
		        wait1 = time.time()
		        wait2 = time.time()
		        wait = (wait2 - wait1)/60
		        while wait < 10 :
		            wait2 = time.time()
			    wait = (wait2 - wait1)/60
			print 'Continuando...'
            soup = BeautifulSoup(s)
            tables = soup('td')
            Found = False
            for t in tables :
                if t.get('align') == "center" and t.get('bgcolor') == "#00387b":
                    strong = t('strong')
                    for stro in strong :
                        #FIRMA INVALIDADA
                        if str(stro.contents[0]).startswith('NO ENCON') :
                            Validar = 0
                            Found = True
                    if Found == False :
                        bold = t('b')
                        for b in bold :
                            if str(b.contents[0]).startswith('DATOS') :
                                #VALIDAR FIRMA
                                Found = True
                                Validar = 1
        data = list()
        for each in (i, Elector, Validar, estado, municipio, parroquia, centro, direccion) : data.append(each)
        #ESCRIBE DATOS EN CSV
        wr.writerow(data)
        count = count + 1
        if count % 500 == 0 :
            print "Espere 2 mins..."
            wait1 = time.time()
            wait2 = time.time()
            wait = (wait2 - wait1)/60
            while wait < 2 :
                wait2 = time.time()
                wait = (wait2 - wait1)/60
            print "Continuando..."
        #TIEMPO ESTIMADO CADA MULTIPLO DE 10
        if count % 10 == 0 : print 'Tiempo estimado:', (time.time() - time_perci)/60 * (len(CI)-CI.index(i)), 'Mins.', "Horas:", ((time.time() - time_perci)/60 * (len(CI)-CI.index(i)))/60

log.close()
elapsed = (time.time() - start_time)/60
print 'Total individuos:', count
print 'End. Minutos:', elapsed
