import re
try:
    from urllib2 import urlopen
    from urlparse import urljoin
except ImportError: # Python 3
    from urllib.parse import urljoin
    from urllib.request import urlopen

from bs4 import BeautifulSoup, SoupStrainer # pip install beautifulsoup4

url = "https://www.hsr.it/dottori"
for count in range(1, 10):
    tag = "00" + str(count)
    only_links = SoupStrainer("a", href=re.compile(tag))
    soup = BeautifulSoup(urlopen(url), parse_only=only_links)
    try :
        print(soup.a.string)
    except AttributeError:
        print()


#print(soup.find_all('a'))
# urls = [urljoin(url, a["href"]) for a in soup(only_links)]
# link = "n".join(urls)

# return link