from flask import Flask, render_template, url_for, request
import xlrd
import requests
from lxml import html
import unicodecsv as csv

app = Flask(__name__)

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
failed = False

workbook = xlrd.open_workbook('Dataset_for_Gifts.xlsx') 	# import values from the dataset
			
masterset = {}												# All the values of data is stored here
sheet_names = ['','Kids','Child','Teenager','Female Adult','Male Adult','Young Adult','Gadgets','Male Clothes','Female Clothes','Sports','Female Accessories','Male Accessories','Male Footwear','Female Footwear','Trail']
category_list = ['Sports','Gadgets','Clothes','Accessories','Footwear']

for index in range(1,workbook.nsheets):						# To find the frequency of each gift
	worksheet = workbook.sheet_by_index(index) 
	dataset = {}
	for row in range(worksheet.nrows):
		for column in range(worksheet.ncols):
			data = worksheet.cell(row,column).value
			if(data!=''):
				if data not in dataset:
					dataset[data] = 1
				dataset[data] += 1
	masterset[sheet_names[index]] = dataset

for index in masterset :									# To find the maximum frequency
	sorted_data = sorted(masterset[index].items(), key=lambda (k,v) : (v,k),reverse=True)
	#sorted_data = dict(sort)
	masterset[index] = sorted_data
	#print index
	#print masterset[index]

@app.route('/home')
def hello_name():
    return render_template('home.html',masterset = masterset, len = len(masterset))


@app.route("/home",methods=["GET","POST"])
def home():
	if request.method == "POST":
		age = request.form["age"]
		gender = request.form["gender"]

	if(age=="kids"):
		category = 'Kids'
	elif(age=='children'):
		category = 'Child'
	elif(age== 'teenager'):
		category = 'Teenager'
	elif(age=='adult'):
		category='Young Adult'
	elif(age=="elderly" and gender=='Female'):
		category = "Female Adult"
	elif(age=='elderly' and gender=='Male'):
		category='Male Adult' 

	return render_template("category.html",gender = gender, category = category,masterset = masterset)


@app.route('/category?=<product_category>/gender?=<gender>')
def view_category(product_category,gender):
	if(product_category in category_list):
		if(product_category in category_list[2::]):
			product_category = gender + " " + product_category
	return render_template("view_product.html",masterset = masterset, product_category = product_category)


@app.route('/product?=<product>')
def view_product(product):
	url = 'https://www.amazon.in/s?k={0}&rh=n%3A1389401031&ref=nb_sb_noss'.format(product)
	scraped_products = []

	print ("Retrieving %s"%(url))
	response = requests.get(url, headers=headers, verify=False)
	parser = html.fromstring(response.text)
	print ("Parsing page")

	product_listings = parser.xpath('//div[contains(@class,"s-result-item")]')

	print product_listings

	for product in product_listings:
		raw_name = product.xpath('.//span[contains(@class,"a-text-normal")]//text()')        # product name
		raw_url = product.xpath('.//a[contains(@class,"a-text-normal")]/@href')
		raw_price = product.xpath('.//span[@class="a-price"]//text()')  #price
        raw_image = product.xpath('.//img[contains(@class,"s-image")]/@src')       # product_image
        #raw_rating = product.xpath('//span[@class="a-icon-alt"]//text()')
        name  = ' '.join(' '.join(raw_name).split())
        image = ' '.join(' '.join(raw_image).split())
        data = {
                    'name': name,
                    'price':raw_price[0][1::],
                    'image':image,
                    'url' : "https://www.amazon.in" + raw_url[0],
                    'website':"amazon"
        }
        scraped_products.append(data)

        if scraped_products:
	        with open('amazon-scraped-data.csv','wb') as csvfile:
	        	fieldnames = ["name","price","image","url","website"]
	        	writer = csv.DictWriter(csvfile,fieldnames = fieldnames,quoting=csv.QUOTE_ALL)
	        	writer.writeheader()
	        	for data in scraped_products:
	        		writer.writerow(data)
    	else:
        	print("No data scraped")

	print scraped_products

	return render_template("recommended_products.html",scraped_products = scraped_products)

if __name__ == '__main__':
   app.run(debug = True)

'''

	kids = 0-5
	children = 6-12
	teenager = 13-19
	adult = 20-31
	elderly = 32 +
  
'''
