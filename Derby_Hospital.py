# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 16:45:21 2021

@author: Gustavo
"""


#!/bin/env python
import sys, signal
import http.server
import socketserver
#new imports
import requests
import urllib.request
import os
import feedparser
import json
import threading 
import cgi
from bs4 import BeautifulSoup, SoupStrainer
import socket

import re
try:
    from urllib2 import urlopen
    from urlparse import urljoin
except ImportError: # Python 3
    from urllib.parse import urljoin
    from urllib.request import urlopen



#manage the wait witout busy waiting
waiting_refresh = threading.Event()

# primi articoli di ogni testata
services = [] 

# Imposta il numero della porta: 8080
link_hospital = "https://www.hsr.it/dottori"
port = 8080

# classe che mantiene le funzioni di SimpleHTTPRequestHandler e implementa
# il metodo get nel caso in cui si voglia fare un refresh

def get_link(href_tag):
    url = link_hospital
    only_links = SoupStrainer("a", href=re.compile(href_tag))
    soup = BeautifulSoup(urlopen(url), parse_only=only_links)
    urls = [urljoin(url, a["href"]) for a in soup(only_links)]
    link = "n".join(urls)
    return link


neuroradiologia=get_link("001")

class ServerHandler(http.server.SimpleHTTPRequestHandler):        
    def do_GET(self):
        # Scrivo sul file AllRequestsGET le richieste dei client     
        with open("GET.txt", "a") as out:
          info = "GET request,\nPath: " + str(self.path) + "\nHeaders:\n" + str(self.headers) + "\n"
          out.write(str(info))
        if self.path == '/refresh':
            resfresh_contents()
            self.path = '/'
        http.server.SimpleHTTPRequestHandler.do_GET(self)
        
def getIp():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    print("L'ip per il sito è:" ,ip)
    return ip
        

ip = getIp();



# ThreadingTCPServer per gestire più richieste

# la parte iniziale è identica per tutti i giornali
header_html = """
<html>
    <head>
        <style>
            h1 {
                text-align: center;
                margin: 0;
            }
            table {width:70%;}
            img {
                max-width:300;
                max-height:200px;
                width:auto;
            }
            td {width: 33%;}
            p {text-align:justify;}
            td {
                padding: 20px;
                text-align: center;
            }
            .topnav {
  		        overflow: hidden;
  		        background-color: #000000;
  		    }
            .topnav a {
  		        float: left;
  		        color: #ffffff;        
  		        text-align: center;
  		        padding: 14px 16px;
  		        text-decoration: none;
  		        font-size: 17px;
  		    }        
  		    .topnav a:hover {
  		        background-color: #ff0022;
  		        color: black;
  		    }        
  		    .topnav a.active {
  		        background-color: #ff0022;
  		        color: black;
  		    }
        </style>
    </head>
    <body>
        <title>Mazzanti hospital services</title>
"""

'''
topnav a -> scritte del menu

'''

# la barra di navigazione è identica per tutti i giornali
navigation_bar = """
        <br>
        <br>
        <br>
        <div class="topnav">
            <a class="active" href="http://{ip}:{port}" style="float: center">Home</a>
  		    <a href="http://{ip}:{port}/pronto_soccorso.html" style="float: center">Pronto soccorso</a>
            <a href="{neuro}" style="float: center">Neurologia</a>
            <a href="http://{ip}:{port}/pediatria.html" style="float: center">Pediatria</a>
            <a href="http://{ip}:{port}/oculistica.html" style="float: center">Oculistica</a>
            <a href="http://{ip}:{port}/cardiologia.html" style="float: center">Cardiologia</a>
            <a href="http://{ip}:{port}/radiologia.html" style="float: center">Radiologia</a>
            <a href="http://{ip}:{port}/psichiatria.html" style="float: center">Psichiatria</a>
  		    <a href="http://{ip}:{port}/refresh" style="float: center">Aggiorna contenuti</a>
            <a href="http://{ip}:{port}/info.pdf" download="info.pdf" style="float: center">Download info pdf</a>
  		</div>
        <br><br>
        <table align="center">
""".format(neuro=neuroradiologia,ip=ip,port=port)

footer_html= """
        </table>
    </body>
</html>
"""


  
# creo tutti i file utili per navigare.
def resfresh_contents():
    print("updating all contents")
    create_pronto_soccorso()
    create_neurologia()
    create_pediatria()
    create_oculistica()
    create_cardiologia()
    create_radiologia()
    create_psichiatria()
    create_index()
    print("finished update")


server = socketserver.ThreadingTCPServer((ip,port), ServerHandler)

# creazione della pagina specifica del sole 24 ore
# prendendo le informazioni direttamente dal feed rss
def create_pronto_soccorso():
    create_page_img_html('http://xml2.corriereobjects.it/rss/homepage.xml', 'images/pronto_soccorso', 'pronto_soccorso.html', 'Pronto soccorso')

# creazione della pagina specifica di Repubblica
# prendendo le informazioni direttamente dal feed rss
def create_neurologia():
    create_page_img_html('http://xml2.corriereobjects.it/rss/homepage.xml', 'images/neurologia', 'neurologia.html', 'Neurologia')

# creazione della pagina specifica del corriere della sera
# prendendo le informazioni direttamente dal feed rss
def create_pediatria():
    create_page_img_html('http://xml2.corriereobjects.it/rss/homepage.xml', 'images/pediatria', 'pediatria.html', 'Pediatria')
    
# creazione della pagina specifica dell' Internazionale
# prendendo le informazioni direttamente dal feed rss
def create_oculistica():
    create_page_img_html('https://www.internazionale.it/sitemaps/rss.xml', 'images/oculistica', 'oculistica.html', 'Oculistica')

# creazione della pagina specifica di Tom's Hardware
# prendendo le informazioni direttamente dal feed rss
def create_cardiologia():
    create_page_img_html('https://www.tomshw.it/feed/', 'images/cardiologia', 'cardiologia.html', 'Cardiologia')

# creazione della pagina specifica di SmartWorld
# prendendo le informazioni direttamente dal feed rss
def create_radiologia():
    create_page_img_html('https://www.smartworld.it/feed', 'images/radiologia', 'radiologia.html', 'Radiologia')


def create_psichiatria():
    create_page_img_html('https://www.smartworld.it/feed', 'images/psichiatria', 'psichiatria.html', 'Psichiatria')
    
# metodo per eseguire l'aggiunga sulla tabella in comune per tutti
def add_element_in_table(i, link, url_images, title, message):
    if (i == 0):
        #il primo articolo di ogni testata va nella pagina di HOME
        services.append('<td><a href="' + link + '"><img src="' + url_images + '"><br><p>'+ title + '</p></a></td>')
    if (i%3 == 0):
        message = message + "<tr>"
    message = message + '<td><a href="' + link + '"><img src="' + url_images + '"><br><p>'+ title + '</p></a></td>'
    if (i%3 == 2):
        message = message + "</tr>"
    return message

# metodo per create una pagina locale, trovando l'img dentro la descrizione
# che è in formato html perciò utilizzo beautifulsoup
# non funziona con tutte le pagine solo le 4 precedenti
def create_page_img_html(feed, image_url, name_page, title):
    r = requests.get(feed)
    if (r.status_code == 200):
        if not os.path.exists(image_url):
            os.makedirs(image_url)
        d = feedparser.parse(r.text)
        message = header_html + "<h1>" + title + "</h1>" + navigation_bar
        # gestione eccezzioni se nel feed rss sono meno di 6 informazioni
        try:
            for i in range(6):
                try:
                    url_images = "./" + image_url + "/" + str(i) + ".jpg"
                    os.remove(url_images)
                except:
                    pass
                soup = BeautifulSoup(d.entries[i].description, features="lxml")
                urllib.request.urlretrieve(soup.find('img')['src'], url_images)
                # utilizzo metodo in comune per aggiungere le info nella tabella
                message = add_element_in_table(i, d.entries[i].link, url_images, d.entries[i].title, message)   
        except:
            pass
        message = message + footer_html
        f = open(name_page,'w', encoding="utf-8")
        f.write(message)
        f.close()
    else:
        print("Errore caricamento contenuti " + title)
    
# creazione della pagina index.html (iniziale)
# contenente i primi articoli di ogni testata giornalistica
def create_index():
    f = open('index.html','w', encoding="utf-8")
    try:
        message = header_html + "<h1>Mazzanti hospital</h1>" + navigation_bar
        message = message + '<tr><th colspan="2"><h2>Servizi</h2></th>'
        message = message + '<tr>' + services[0] + services[1]
        message = message + services[4] + "</tr>"
        message = message + '<tr>' + services[2] + services[3]
        message = message + services[5] + "</tr>"
        message = message + footer_html
    except:
        pass
    f.write(message)
    f.close()

   

# definiamo una funzione per permetterci di uscire dal processo tramite Ctrl-C
def signal_handler(signal, frame):
    print( 'Exiting http server (Ctrl+C pressed)')
    try:
      if(server):
        server.server_close()
    finally:
      # fermo il thread del refresh senza busy waiting
      waiting_refresh.set()
      sys.exit(0)
      
# metodo che viene chiamato al "lancio" del server
def main():
    resfresh_contents()
    #Assicura che da tastiera usando la combinazione
    #di tasti Ctrl-C termini in modo pulito tutti i thread generati
    server.daemon_threads = True 
    #il Server acconsente al riutilizzo del socket anche se ancora non è stato
    #rilasciato quello precedente, andandolo a sovrascrivere
    server.allow_reuse_address = True  
    #interrompe l'esecuzione se da tastiera arriva la sequenza (CTRL + C) 
    signal.signal(signal.SIGINT, signal_handler)
    # cancella i dati get ogni volta che il server viene attivato
    f = open('AllRequestsGET.txt','w', encoding="utf-8")
    f.close()
    # entra nel loop infinito
    try:
      while True:
        server.serve_forever()
    except KeyboardInterrupt:
      pass
    server.server_close()

if __name__ == "__main__":
    main()
