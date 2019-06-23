import argparse
import requests
import unicodecsv as csv
from lxml import html


def parse(product):

    url = 'https://www.snapdeal.com/search?keyword={0}'.format(product)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    failed = False

    # Retries for handling network errors
    for _ in range(5):
        print ("Retrieving %s"%(url))
        response = requests.get(url, headers=headers, verify=False)
        parser = html.fromstring(response.text)
        print ("Parsing page")

        if response.status_code!=200:
            failed = True
            continue
        else:
            failed = False
            break

    if failed:
        return []

    product_listings = parser.xpath('//div[contains(@class,"product-tuple-listing")]')
    scraped_products = []

    print product_listings

    for product in product_listings:
        raw_name = product.xpath('.//p[contains(@class,"product-title")]/text()')        # product name
        raw_price = product.xpath('.//span[contains(@class,"product-price")]//text()')  #price
        raw_url = product.xpath('.//div[contains(@class,"product-tuple-description")]//a/@href')       # product_image
        #raw_rating = product.xpath('//spdp-widget-link noUdLine hashAddedan[@class="a-icon-alt"]//text()')
        raw_image = product.xpath('.//div[contains(@class,"product-tuple-image")]//a//source[contains(@class,"product-image")]/@srcset')

        name  = ' '.join(' '.join(raw_name).split())
        price  = ' '.join(' '.join(raw_price).split())
        price = int(price.replace(" ","").replace(",","").replace("Rs.",""))
        image = ' '.join(' '.join(raw_image).split())
        print type(price)
        data = {
                    'name':name,
                    'price':price,
                    'image':image,
                    'url':raw_url[0],
                    'website':"snapdeal"
        }
        scraped_products.append(data)
    return scraped_products


if __name__=="__main__":

    product = raw_input("product : ")

    scraped_data =  parse(product)
    if scraped_data:
        print ("Writing scraped data to snapdeal-scraped-data.csv")
        with open('snapdeal-scraped-data.csv','wb') as csvfile:
            fieldnames = ["name","price","image","url","website"]
            writer = csv.DictWriter(csvfile,fieldnames = fieldnames,quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for data in scraped_data:
                writer.writerow(data)
    else:
        print("No data scraped")




#https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=apple&_sacat=0&LH_TitleDesc=0&_osacat=0&_odkw=mobile+phones&LH_TitleDesc=0

#https://www.ebay.com/sch/i.html?_from=R40&_nkw=apple&_sacat=0&LH_TitleDesc=0&LH_TitleDesc=0&_pgn=2

# amazon

#s-search-results >> span class="rush-component s-latency-cf-section"

#product << div class = "some code for each product " << div class="s-result-list s-search-results sg-row"



'''


    ---- Path of main products for ebay----
<div class = "srp-main srp-main--isLarge"
<div id = "mainContent"
    <div class = srp-river srp-layout-inner"
        <div id = "srp-river-main"
            <div id = "srp-river-results"
                <ul class = "srp-results srp-lists clearfix">
                    <div id ="srp-river-results-listing(123456..)">


    ---- Path of main product for amazon ----




'''
