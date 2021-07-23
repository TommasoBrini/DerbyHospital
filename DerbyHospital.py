# -*- coding: utf-8 -*-
"""
Progetto di Programmazione di Reti 2021
Autori: Mazzanti Gustavo - Brini Tommaso
Matricole: 0000914975 - 0000933814
"""

#Imports
import sys, signal
import http.server
import socketserver
import random
import socket
import re
from bs4 import BeautifulSoup, SoupStrainer
try:
    from urllib2 import urlopen
    from urlparse import urljoin
except ImportError: # Python 3
    from urllib.parse import urljoin
    from urllib.request import urlopen

#Istanziato l'array per le row della table html dei servizi
services = [] 

#dizionario con le immagini per i servizi
images = {
    '1': '/images/ospedale/agg.jpg',
    '2': '/images/ospedale/agg1.png',
    '3': '/images/ospedale/agg2.jpg',
    '4': '/images/ospedale/agg3.jpg'
    }

# link della pagina con tutti i servizi dell'ospedale San Raffaele
link_hospital = "https://www.hsr.it/dottori"

# Imposta il numero della porta: 8080
port = 8080


# Metodo che cerca i link dei vari servizi dell'ospedale San Raffale
# dal link_hospital, ispezionando l'html di questa
def getLink():
    url = link_hospital
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
        if self.path == '/refresh':
            resfresh_contents()
            self.path = '/'
        http.server.SimpleHTTPRequestHandler.do_GET(self)

#Metodo che restituisce l'ip corrente della macchina su cui viene avviato il programma
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
        
#Viene salvato l'ip corrente nella variabile ip
ip = getIp();

#Header valido per tutte le pagine html
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

#Barra del menu univoca per tutte le pagine html
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

#Footer univoco per tutte le pagine html
footer_html= """
        </table>
    </body>
</html>
"""

#Metodo che carica i servizi dal link_hospital e genera la pagina servizi.html
def resfresh_contents():
    print("Started update")
    load_services()
    create_service()
    print("Finished update")

#Apertura della socket sull'ip locale della macchina corrente e alla porta di default
server = socketserver.ThreadingTCPServer((ip,port), ServerHandler)

#Metodo che richiama add_service() per tutti i servizi dentro al dizionario
def load_services():
    dizionario=getLink()
    c=0
    while c<9:
        name,link=dizionario.get(c)
        add_service(link, name)
        c+=1

#Metodo che aggiunge all'array services la row della table html della pagina servizi.html
def add_service(link, name):
    image = images.get(str(random.randint(1,4)))
    service = str('<td><a href="{link}"><img src="{image}"><br><p>{name}</p></a></td>'.format(link=link,image=image,name=name))
    services.append(service)

#Metodo che genera la pagina servizi.html con tutti i servizi presenti nell'array services
def create_service():
    f = open('servizi.html','w', encoding="utf-8")
    row = header_html + '<h1>Derby hospital</h1>' + navigation_bar
    row = row + '<tr><th colspan="3"><h2>Servizi</h2></th>'
    for i in range(0,8,3):
        row = row + '<tr>'+ services[i] + services[i+1] + services[i+2] + '</tr>'
    image = images.get(str(random.randint(1,4)))
    row = row + '<tr><td></td><td><a href="https://www.hsr.it/dottori?"><img src="{image}"><br><p>Tutti i servizi</p></a></td>'.format(image=image)
    f.write(row)
    f.close()

#Metodo che genera la pagina index.html
def create_index():
    f = open('index.html','w', encoding="utf-8")
    table = header_html + "<h1>Derby hospital</h1>" + navigation_bar
    table = table + '<tr><th colspan="3"><h2>Home</h2></th>'
    table = table + '<tr><td><a href="https://www.hsr.it/"><img src="/images/ospedale/SanRaffaele.png"><br><p>SanRaffaele</p></a></td>'
    table = table + '<td><a href="https://www.hsr.it/prenotazioni"><img src="/images/ospedale/prenota-ora.png"><br><p>Prenotazioni</p></a></td>'
    table = table + '<td><a href="https://www.hsr.it/chi-siamo"><img src="/images/ospedale/chi_siamo.jpg"><br><p>Chi siamo</p></a></td></tr>'
    table = table + '<tr><td><a href="https://www.hsr.it/strutture"><img src="/images/ospedale/sedi.jpg"><br><p>Le nostre sedi</p></a></td>'
    table = table + '<td><a href="http://{ip}:{port}/servizi.html"><img src="/images/ospedale/servizi.png"><br><p>Servizi</p></a></td>'.format(ip=ip, port=port)
    table = table + '<td><a href="https://www.hsr.it/news"><img src="/images/ospedale/news.jpg"><br><p>News</p></a></td></tr>'
    f.write(table)
    f.close()

#Metodo che gestisce l'arresto da riga di comando
def signal_handler(signal, frame):
    print('Exiting (Ctrl+C pressed)')
    try:
      if(server):
        server.server_close()
    finally:
      sys.exit(0)

#main del programma
def main():
    #Al primo avvio vengono caricati i services e viene generata sercizi.html
    resfresh_contents()
    #Generazione index.html
    create_index()
    #Si occupa di gestire la terminazione da tastiera,
    #assicurandosi che tutti i thread vengano terminati corretamente
    server.daemon_threads = True 
    #Sovrascrive la socket vecchia (che ancora non è chiusa) nel caso ce ne sia una nuova
    server.allow_reuse_address = True  
    #interrompe il programma quando viene premuto "CTRL + C" 
    signal.signal(signal.SIGINT, signal_handler)
    # f = open('GETRequest.txt','w', encoding="utf-8")
    # f.close()
    try:
      while True:
        server.serve_forever()
    except KeyboardInterrupt:
      pass
    server.server_close()

if __name__ == "__main__":
    main()
