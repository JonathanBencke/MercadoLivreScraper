import bs4
import requests
import smtplib
import time
import json
from datetime import datetime

# Itens Mercado Livre:
searchTerm = 'Macbook-pro-2010'
link = 'https://lista.mercadolivre.com.br/'+searchTerm+'_DisplayType_LF'
headers = {'referer': 'https://www.google.com/', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'}

def getValueFromElement(element, type, className):
    try:
        return element.find(type, className).text.strip()
    except:
        return ''

def getPrice(div):
    discount = div.find('div', 'price-tag discount-arrow arrow-left')
    elems = div.find('span', 'price-tag')
    pricen_str = elems.text.strip()
    pricen_str = pricen_str.replace('.', '')
    pricen_str = pricen_str.replace(',', '.')
    pricen_str = pricen_str.replace('\n', '')
    price = float(pricen_str[2:])
    if discount != None:
        discount = discount.text.strip()
        discount = float(discount[:2])/100
        price = price * (1-discount)
    return price

def startCrawling(page, products):
    res = requests.get(page, headers=headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    divs = soup.findAll('div', 'andes-card andes-card--flat andes-card--default ui-search-result ui-search-result--core andes-card--padding-default')
    for div in divs:
        product = {}
        product['price'] = getPrice(div)
        product['link'] = div.find('a', href=True)['href']
        product['name'] = getValueFromElement(div, 'h2', 'ui-search-item__title')
        product['condicao'] = getValueFromElement(div, 'span', 'ui-search-item__group__element ui-search-item__details')
        product['itemId'] = div.find('input', attrs={'name':'itemId', 'type':'hidden'})['value']
        product['img_src'] = div.find('img', 'ui-search-result-image__element')['data-src']
        product['frete'] = getValueFromElement(div, 'p', 'ui-search-item__shipping ui-search-item__shipping--free')
        products[product['itemId']] = product
    
def getPages(currentLink, links):
    links.append(currentLink)
    res = requests.get(currentLink, headers=headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    nextBtn = soup.find('li', 'andes-pagination__button andes-pagination__button--next')
    if nextBtn is not None:
        nextLink = nextBtn.find('a', href=True)['href']
        if nextLink is not None:
            print('Next page link found: ', nextLink)
            getPages(nextLink, links)

def exportCsv(products):
    filename = './dumps/'+datetime.today().strftime('%Y%m%d')+'_exported.json'
    with open(filename, 'a+') as fp:
        fp.seek(0)
        data = fp.read(100)
        if len(data) > 0 :
            fp.write("\n")
        fp.write(json.dumps(products))
    print('Dump json created at ',filename)

def main():
    links = []
    print('Start execution')
    print('Getting all page links')
    getPages(link, links)
    products = {}
    print('Start Crawling')
    for currentLink in links:
        print('Crawling: ', currentLink)
        startCrawling(currentLink, products)
        print(len(products), ' products crawled!')
    exportCsv(products)

def mainDev():
    products = {}
    startCrawling('https://informatica.mercadolivre.com.br/portateis-e-acessorios-notebook/apple/macbook-pro/16-a-64-GB/macbook-pro-2010_CustoFrete_Gratis_DisplayType_LF_NoIndex_True', products)
if __name__ == "__main__":
    main()