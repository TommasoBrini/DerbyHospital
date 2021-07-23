import re
try:
    from urllib2 import urlopen
    from urlparse import urljoin
except ImportError: # Python 3
    from urllib.parse import urljoin
    from urllib.request import urlopen

from bs4 import BeautifulSoup, SoupStrainer # pip install beautifulsoup4

def getLink():
    url = "https://www.hsr.it/dottori"
    count = 0
    c = 0
    dizionario={}
    while count<21:
        if c<10:
            tag = "00" + str(c)
        elif c<100:
            tag = "0" + str(c)
        else:
            tag = str(count)
        
        only_links = SoupStrainer("a", href=re.compile(tag))
        soup = BeautifulSoup(urlopen(url), parse_only=only_links)
        urls = [urljoin(url,a["href"]) for a in soup(only_links)]
        link = "n".join(urls)
        c+=1
        try :
            count+=1
            dizionario[count]=soup.a.string, soup.a.link
        except AttributeError:
            c=c
    return dizionario

    
    
        


#print(soup.find_all('a'))
# urls = [urljoin(url, a["href"]) for a in soup(only_links)]
# link = "n".join(urls)

# return link