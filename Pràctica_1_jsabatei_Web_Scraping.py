# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 17:45:10 2019

@author: Josep Maria Sabaté

Master en Ciència de Dades

Assignatura: Tipologia i cicle de vida de les Dades

Pràctica 1: Web Scraping

Bibliografia: 
    "Web Scraping". Laia Subirats i Mireia Calvo. UOC PID_00256968 
    "Web Scraping with Python". Autor: Richard Lawson. Packt Publishing
    
"""
import csv
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# Funció per a llegir una adreça URL donada
def descarrega_url(url, intents=2):
    try:
        html = requests.get(url)
#        print(html)
    except html.status_code as e:
        print ('Error al llegir la pàgina:', e.reason)
        html = None
        if intents > 0:
            if 500 <= html.status_code < 600: # tornar a intentar-ho per a errors 5xx
                return descarrega_url(url, intents-1)
            else:
                exit ("Errors no 500 al carregar la pàgina. S'atura el script")
        else:
            exit ("Error de càrrega després d'intentar-ho dues vegades")
    pagina = BeautifulSoup (html.content, features="lxml")
    print ("S'ha llegit la pàgina ", url)        
    return pagina


# ####################################################
# PAS 1. Llegir les 6 pàgines sobre els resultats de les eleccions locals.
# A la pàgina: https://www.bcn.cat/estadistica/catala/dades/telec/loc/index.htm
# S'observa tota la informació que publica l'Ajuntament de Barcelona sobre
# les eleccions locals.
# Una anàlisi d'aquesta pàgina mostra que és només a partir de l'any 2011
# quan es disposa dels resultats desglossats per seccions censals
# Es disposa, així, del resultat de les eleccions locals del 2011, 2015 i 2019
# Per a cada any es farà web scraping d'aquesta web per a descarregar:
# - La relació de candidatures de cada any (3 fitxers)
# - Els resultats per secció censal de cada any (3 fitxers)
# ####################################################

print ("Inici del procés Web Scraping de recuperació d'informació numérica de les" +
       " eleccions local de l'Ajuntament de Barcelona anys 2011, 2015 i 2019")   

# Totes les pàgines tenen la mateixa url arrel amb nom de taula final diferent
arrel = "https://www.bcn.cat/estadistica/catala/dades/telec/loc/"

# Les 3 primeres taules corresponen als noms de les candidutaures dels anys
# 2019, 2015 i 2011 respectivament.
# La 4ª a la 6ª taula corresponen als resultats pròpiament dits

taules = ["loc19/t24.htm", "loc15/cloc1517.htm", "loc11/cloc1117.htm",
          "loc19/t310.htm", "loc15/cloc1599.htm", "loc11/cloc1199.htm"]
pagina = []
for taula in taules:
    url = arrel + taula
    pagina.append(descarrega_url (url))

# ####################################################
# FI PAS1. Fi de la lectura de les 6 taules. 
# La llista "pagina" contè les 6 pàgines descrites
# ####################################################

# ####################################################
# PAS 2. Extracció d'informació de les pàgines, noms columnes
#        Els noms de les columnes estan  una taula, etiqueta td i class = WhadsColVar1
# ####################################################

nom_columnes = []
for k in range(6):           # per a cadascuna de les 6 pàgines
    nom_columnes.append([])  # afegir una subllista a nom_columnes
    for titol in pagina[k].find_all("td"):   
        x = titol.get("class")
        if x != None and x[0] == 'WhadsColVar1':  
            nom_columnes[k].append(titol.string)

# ####################################################
# FI PAS2. Fi Extracció d'informació de les pàgines, noms columnes 
# La llista de llistes "nom_columnes" contè les 6 capçaleres
# ####################################################

# ####################################################
# PAS 3. Neteja de les dades de les capçaleres
# ####################################################
            
# De l'observació visual, alguns nom_columnes s'han inicialitzat amb None
# Per alguna raó, titol.string deu tornar None quan aquest contingut té 
# un salt de línia, <br/>, com a "titol.string,
# com es veu si es revisen les etiquetes td amb class WhadsColVar1.
# S'arreglen manualment aquest casos indicant el nom de la columna a partir de
# l'observació visual de la pàgina
# Preveient que això pugués canviar en el futur, es preveu donar un error.
# si no coincideix l'element de llista concret identificat visualment
# amb el valor None.
if nom_columnes[3][23] == None:
    nom_columnes[3][23] = "UNIDOS SI"
else:
    print ("error")
if nom_columnes[3][34] == None:
    nom_columnes[3][34] = "Partit més votat"
else:
    print ("error")

if nom_columnes[4][10] == None:
    nom_columnes[4][10] = "VOX - PFYV"
else:
    print ("error")
if nom_columnes[4][15] == None:
    nom_columnes[4][15] = "FE de las JONS"
else:
    print ("error")
if nom_columnes[4][17] == None:
    nom_columnes[4][17] = "Millor Barcelona"
else:
    print ("error")

# Així mateix, de l'observació visual de nom_columnes, s'observa que molts dels elements
# de la llista tenen blancs amb format unicode: "xa0". Es reemplaça aquest codi.        
for k in range(6):
    nom_columnes[k] = [x.replace(u"\xa0", "") for x in nom_columnes[k]]

# ####################################################
# FI PAS 3. Neteja de les dades de les capçaleres
# ####################################################

# ####################################################
# PAS 4. Extracció d'informació de les pàgines, contingut de cada fila
# de cada taula.
# ####################################################
     
dades   = []
for k in range(6):
    dades.append ([])
    taula   = pagina[k].find_all("table")
    if len(taula) !=1:
        print ("Tipus error: hi ha o zero taules o més d'una taula, cas no previst")
    for html_fila in taula[0].find_all("tr"):
        fila    = []
        for col in html_fila.find_all ("td"):
            x = col.get("class")
            if x != None and (x[0] == 'WhadsDades' or x[0] == 'WhadsRowVar1'):
                fila.append(col.string)
        if len(fila) != 0:      # evtar les files en blanc
            dades[k].append(fila)
                

# ####################################################
# FI PAS 4. Extracció d'informació de les pàgines, contingut de les columnes
# La llista de llistes "dades" contè el contingut de les 6 taules
# ####################################################
        
# ####################################################
# PAS 5. Neteja de les dades contingut de les taules
# ####################################################
            
# De l'observació visual, algun contingut de columnes s'han inicialitzat amb None
# Per alguna raó, col.string deu tornar None quan aquest contingut té 
# un salt de línia, <br/>, com a "col.string",
# com es veu si es revisen les etiquetes td amb class WhadsDades.
# S'arreglen manualment aquest casos identificant la cel·la a modificar
# a partir de l'observació visual de la pàgina
# Preveient que això pugués canviar en el futur, es preveu donar un error
# si no són els casos identificats a la data.
if dades[0][3][1] == None:
    dades[0][3][1] = "ESQUERRA REPUBLICANA-ERNEST MARAGALL ALCALDE+BARCELONA-NOVA-ACORD MUNICIPAL"
else:
    print ("error")
if dades[0][6][1] == None:
    dades[0][6][1] = "PARTIT DELS SOCIALISTES DE CATALUNYA-COMPROMÍS PER BARCELONA-UNITS-CANDIDATURA DE PROGRÉS"
else:
    print ("error")

# Així mateix, de l'observació visual de nom_columnes, s'observa que molts dels elements
# de la llista tenen blancs amb format unicode: "xa0". Es reemplaça aquest codi.        
# Un cop reemplaçats, es comprova, així mateix que no hagi cap fila amb totes
# les columnes en blanc (utilitzada a la corresponent pàgina com a element separador)
dades_netes = []
for k in range(6):
    dades_netes.append([])
    for kk in range(len(dades[k])):
        y = [x.replace(u"\xa0", "") for x in dades[k][kk]]
        if "".join(y) != "":
            dades_netes[k].append(y)

# ####################################################
# FI PAS 5. Neteja de les dades del contingut de les taules
# ####################################################


# ####################################################
# PAS 6. Validacions creuades entre noms de columnes i dades.
# ####################################################
            
# Sobserva que la taula de la relació de candidatures de l'any 2011
# Les pàgines 2011 de candidatures i resultats estan respectivament a nom_columnes[2] i dades_netes[2]
# (Columna 1 de nom_columnes[2] i també columna 1 dades_netes[2][<cada fila>])
# és una columna en blanc.  
# s'esborra la columna de les taules que conformen la relació de candidatures
# nom_columnes [2] i dades_netes[2]<cada fila>            

nom_columnes[2] = [nom_columnes[2][0], nom_columnes[2][2]]
dades_netes[2] = [[dades_netes[2][x][0], dades_netes[2][x][2]] for x in range(len(dades_netes[2]))]

# Control de que per a cada taula, de cada fila de detall recuperada, 
# el seu número de columnes és correcte i no hi ha cap inconsistència a la pàgina
for k in range(6):
    for y in dades_netes[k]:
        if len(y) != len(nom_columnes[k]):
            print ("error a la fila: ", y, ". No té el nombre de columnes: ", len(nom_columnes[k]))
            print (len(y), len(nom_columnes[k]))


# ####################################################
# FI PAS 6. Esborrar una columna de les taules de l'any 2015.
# ####################################################


# ####################################################
# PAS 7. Gravar els fitxers csv
# ####################################################

nom_fitxers = ["Eleccions_locals_Barcelona_20190526_Candidatures.csv",
               "Eleccions_locals_Barcelona_20150524_Candidatures.csv",
               "Eleccions_locals_Barcelona_20110522_Candidatures.csv",
               "Eleccions_locals_Barcelona_20190526_Resultats.csv",
               "Eleccions_locals_Barcelona_20150524_Resultats.csv",
               "Eleccions_locals_Barcelona_20110522_Resultats.csv"]

# Creació dels 6 fitxers de sortida
for k in range(6):
    path_nom = Path.cwd() / "Estudi Eleccions Locals" / nom_fitxers[k]
    with open(path_nom, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow (nom_columnes[k])
        for fila in dades_netes[k]:
            spamwriter.writerow(fila)
            
print ("Ha finalitzat el procés Web Scraping de recuperació d'informació numérica de les" +
       " eleccions local de l'Ajuntament de Barcelona anys 2011, 2015 i 2019")

# ####################################################
# Recuperació d'imatges
# ####################################################

# S'observa que la mateixa Web de l'Ajuntament de Barcelona, conté imatges de les 
# eleccions locals de Barcelona any 2019. Imatges per barris i seccions censals de:
# -1- Mapes de participació 
# -2- 1r. partir més votat
# -3- Segons partit més votat
# -4- Implantació de les principals candidatures

# Llegir les pàgines (4) amb les imatges desitjades, corresponents als 4 grups anteriors
# "pagina" serà una llista de 4 elements on cada element és la pàgina recuperada.

print ("Inici procés Web Scraping de recuperació d'imatges de les" +
       " eleccions local de l'Ajuntament de Barcelona any 2019")            
            
def descarrega_imatges (url):
    img = requests.get (url, stream = True)
    if img.status_code == 200:
        aSplit   = url.split("/")
        path_nom = Path.cwd() / "Estudi Eleccions Locals" / aSplit[len(aSplit)-1]
        print (path_nom)
        output = open(path_nom, "wb")
        for codi in img:
            output.write (codi)
        output.close()


taules = ["loc19/t311.htm", "loc19/t312.htm", "loc19/t313.htm", "loc19/t314.htm"]
pagina = []
for taula in taules:
    url = arrel + taula
    pagina.append(descarrega_url (url))

imatges   = []
for k in range(len(taules)):
    i = 0
    for img in pagina[k].findAll("img"):
        url  = arrel + "loc19/" + img.get("src")
#        print (url)
        descarrega_imatges(url)
        i += 1
    print ("A la pàgina ", k, " hi ha ", i, "imatges")
    

print ("Final procés Web Scraping de recuperació d'imatges de les" +
       " eleccions local de l'Ajuntament de Barcelona any 2019")           

print ("Fi de l'exercici")

# Fi de l'exercici Web Scraping
            
# Nota:
# a efectes de comprovació, codi suggerit per a llegir els fitxers
# Per exemple el fitxer k
# k = 5
# path_nom = Path.cwd() / "Estudi Eleccions Locals" / nom_fitxers[k]

# with open (path_nom, newline="") as csvfile:
#     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#     i = 0
#     for row in spamreader:
#          print (row)
#          i += 1
#     print (i)
#
# En quant a les imatges es troben al mateix path, el nom de la imatge segueix la pauta:
# -1- Mapes de participació 
#       part_barris.png      Mapa de participació per barris 
#       part_sc.png          Mapa de participació per seccions censals
# -2- 1r. partir més votat
#       pguany_barris.png    Mapa de partit més votat per barris 
#       pguany_sc.png        Mapa de partit més votat per seccions censals
# -3- Segon partit més votat
#       pguany_barris2.png   Mapa de segon partit més votat per barris 
#       pguany_sc2.png       Mapa de segon partit més votat per seccions censals
# -4- Implantació de les principals candidatures
#       xxx_barris.png       Mapa d'implantació de la candidatura xxx (erc, bc, psc, ...) per barris 
#       xxx_sc.png           Mapa d'implantació de la candidatura xxx per seccions censals
#