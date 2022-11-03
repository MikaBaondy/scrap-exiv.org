from collections import deque
from concurrent.futures import process
import requests 
from bs4 import BeautifulSoup

# get lists of table
def get_lists(url, ct):
    tdList, result = [], []
    count = 1
    new_url = f"https://exiv2.org/{url}"
    new_urltxt = requests.get(new_url).text
    new_soup = BeautifulSoup(new_urltxt, 'html.parser')
    for item in new_soup.find_all('td'):
        tdList.append(item.text)
        if count % ct == 0:
            result.append(tdList)
            tdList = list()
        count += 1
    return result

# get html text   
def html_parser():
    collection = list()
    url = "https://exiv2.org/metadata.html"
    rq = requests.get(url).text
    soup = BeautifulSoup(rq, "html.parser")
    for s in soup.find_all('a', href=True):
        collection.append(s['href'])
    return [cItem for c, cItem in enumerate(collection) if c > 10]

# separate ident
def separate_ident(ident):
    ident = ident.split(".")
    return ident[1], ident[2]

# get iptc values
def get_iptc_values():
    url = "iptc.html"
    iptc_list = get_lists(url=url, ct=9)   
    items = [i[2] for i in iptc_list]
    for i in items:
        yield separate_ident(i)
        
# get xmp values
def get_xmp_values():
    def get_type(link):
        ow = link[:-5].split("-")
        return ow[2]
    def get_data(link):
        url = f"https://exiv2.org/{link}"
        urltxt = requests.get(url).text
        soup = BeautifulSoup(urltxt, "html.parser")
        result = [item.text for i, item in enumerate(soup.find_all('td')) if i % 6 == 0]
        return result
    all_link = [h for h in html_parser() if "xmp" in h]
    for a in all_link:
        yield {get_type(a) : get_data(a)}    

# get exiv values
def get_exiv_values():
    all_link = [h for h in html_parser() if "tags" in h and "xmp" not in h]
    for a in all_link:
        lists_ = get_lists(a, 6)
        lists = [l[3] for l in lists_]
        for i in lists:
            yield(separate_ident(i))


######### Ecriture dans le fichier ############
class Ecriture:
    def __init__(self) -> None:
        self.filename = "data.py"
        self.functions = {
                            get_iptc_values(),
                            get_xmp_values(),
                            get_exiv_values()
                         }
    
    def process(self):
        RESULT = deque()
        for function in self.functions:
            RESULT.append(self.uniformize(function))
            print(RESULT)
        return RESULT
    
    def uniformize(self, item): # Mamamdika en dictionnaire
        result = dict()
        try:
            for i in item:
                print(i)
                if i[0] in result:
                    result[i[0]].append(i[1])
                else:
                    result[i[0]] = [i[1]]
            return result
        except:
            return list(item)[0]

if __name__ == "__main__":
    app = Ecriture()
    proceed = app.process()
    print(proceed[0])