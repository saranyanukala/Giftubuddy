import requests
import unicodecsv as csv
from lxml import html

def parse(product):

    url = 'https://www.amazon.in/s?k={0}&rh=n%3A1389401031&ref=nb_sb_noss'.format(product)
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

    product_listings = parser.xpath('//div[contains(@class,"s-result-item")]')
    scraped_products = []


    for product in product_listings:
        raw_name = product.xpath('.//span[contains(@class,"a-text-normal")]//text()')        # product name
        raw_url = product.xpath('.//a[contains(@class,"a-text-normal")]/@href')
        raw_price = product.xpath('.//span[@class="a-price"]//text()')  #price
        raw_image = product.xpath('.//img[contains(@class,"s-image")]/@src')       # product_image
        #raw_rating = product.xpath('//span[@class="a-icon-alt"]//text()')
        name  = ' '.join(' '.join(raw_name).split())
        image = ' '.join(' '.join(raw_image).split())
        if(raw_price):

            price = int(raw_price[0][1::])
            print type(price)
            data = {
                       'name': name,
                        'price':raw_price[0][1::],
                        'image':image,
                        'url' : "https://www.amazon.in" + raw_url[0],
                        'website':"amazon"
            }
        scraped_products.append(data)
    return scraped_products


if __name__=="__main__":

    product = raw_input("Porduct : ")

    scraped_data =  parse(product)
    if scraped_data:
        print ("Writing scraped data to amazon-scraped-data.csv")
        with open('amazon-scraped-data.csv','wb') as csvfile:
            fieldnames = ["name","price","image","url","website"]
            writer = csv.DictWriter(csvfile,fieldnames = fieldnames,quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for data in scraped_data:
                writer.writerow(data)
    else:
        print("No data scraped")

