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

def getLink():
    url = "https://www.hsr.it/dottori"
    count = 0
    c = 0
    dizionario={}
    while count<9:
        if c<10:
            tag = "00" + str(c)
        elif c<100:
            tag = "0" + str(c)
        else:
            tag = str(count)
        
        only_links = SoupStrainer("a", href=re.compile(tag))
        soup = BeautifulSoup(urlopen(url), parse_only=only_links,features="lxml")
        urls = [urljoin(url,a["href"]) for a in soup(only_links)]
        link = "n".join(urls)
        c+=1
        try :
            dizionario[count]= str(soup.a.string), str(link)
            count+=1
        except AttributeError:
            c=c
    return dizionario



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
        <title>Derby hospital services</title>
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
  		    <a href="https://www.hsr.it/" style="float: center">San Raffaele</a>
            <a href="https://www.hsr.it/prenotazioni" style="float: center">Prenotazioni</a>
            <a href="https://www.hsr.it/chi-siamo" style="float: center">Chi Siamo</a>
            <a href="https://www.hsr.it/strutture" style="float: center">Le nostre sedi</a>
            <a href="http://{ip}:{port}/servizi.html" style="float: center">Servizi</a>
            <a href="https://www.hsr.it/news" style="float: center">News</a>
  		    <a href="http://{ip}:{port}/refresh" style="float: center">Aggiorna contenuti</a>
            <a href="http://{ip}:{port}/info.pdf" download="info.pdf" style="float: center">Download info pdf</a>
  		</div>
        <br>
        <br>
        
        <table align="center">
""".format(ip=ip,port=port)

footer_html= """
        </table>
    </body>
</html>
"""


  
# creo tutti i file utili per navigare.
def resfresh_contents():
    print("updating all contents")
    load_services()
    create_service()
    create_index()
    print("finished update")


server = socketserver.ThreadingTCPServer((ip,port), ServerHandler)

# creazione della pagina specifica del sole 24 ore
# prendendo le informazioni direttamente dal feed rss
def load_services():
    # create_page_img_html('http://xml2.corriereobjects.it/rss/homepage.xml', 'images/pronto_soccorso', 'servizi.html', 'Servizi')
    dizionario=getLink()
    c=0
    while c<9:
        name,link=dizionario.get(c)
        add_service(link, name)
        c+=1


# metodo per eseguire l'aggiunga sulla tabella in comune per tutti
def add_service(link, name):
    service = str('<td><a href="{link}"><p>{name}</p></a></td>'.format(link=link,name=name))
    services.append(service)

def create_service():
    f = open('servizi.html','w', encoding="utf-8")
    message = header_html + '<h1>Derby hospital</h1>' + navigation_bar
    message = message + '<tr><th colspan="3"><h2>Servizi</h2></th>'
    for i in range(0,8,3):
        message = message + '<tr>'+ services[i] + services[i+1] + services[i+2] + '</tr>'
    message = message + '<tr><td></td><td><a href="https://www.hsr.it/dottori?"><p>Altro</p></a></td>'
    f.write(message)
    f.close()


    
# creazione della pagina index.html (iniziale)
# contenente i primi articoli di ogni testata giornalistica
def create_index():
    f = open('index.html','w', encoding="utf-8")
    message = header_html + "<h1>Derby hospital</h1>" + navigation_bar
    message = message + '<tr><th colspan="3"><h2>Home</h2></th>'
    message = message + '<tr><td><a href="https://www.hsr.it/"><img src="/images/ospedale/SanRaffaele.png"><br><p>SanRaffaele</p></a></td>'
    message = message + '<td><a href="https://www.hsr.it/prenotazioni"><img src="/images/ospedale/prenota-ora.png"><br><p>Prenotazioni</p></a></td>'
    message = message + '<td><a href="https://www.hsr.it/chi-siamo"><img src="/images/ospedale/chi_siamo.jpg"><br><p>Chi siamo</p></a></td></tr>'
    message = message + '<tr><td><a href="https://www.hsr.it/strutture"><img src="/images/ospedale/sedi.jpg"><br><p>Le nostre sedi</p></a></td>'
    message = message + '<td><a href="http://{ip}:{port}/servizi.html"><img src="/images/ospedale/servizi.png"><br><p>Servizi</p></a></td>'.format(ip=ip, port=port)
    message = message + '<td><a href="https://www.hsr.it/news"><img src="/images/ospedale/news.jpg"><br><p>News</p></a></td></tr>'
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
