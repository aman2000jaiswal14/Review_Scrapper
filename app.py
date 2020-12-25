import os
from flask import Flask,render_template,request

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from flask_cors import cross_origin
import requests

app = Flask(__name__)

@app.route('/',methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')

@app.route('/review',methods=['GET','POST'])
@cross_origin()
def index():
    if(request.method=="POST"):
        try:
            searchString = request.form['content'].replace(" ","")
            searchString = searchString.replace("(","")
            searchString = searchString.replace(")", "")

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = urlopen(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()

            flipkart_html = bs(flipkart_page,'html.parser')

            bigbox = flipkart_html.findAll('div', {"class":"_2pi5LC col-12-12"})

            del bigbox[0:2]
            box = bigbox[0]

            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']


            prodRes = requests.get(productLink)
            prodHtml = bs(prodRes.text,'html.parser')

            review_box = prodHtml.findAll('div',{'class':"col _2wzgFH"})

            # print(len(review_box))

            all_review = []
            count = 1
            for rev in review_box:
                final = {}
                try:
                    final["time"] = rev.find_all('div',{"class":"row _3n8db9"})[0].div.find_all('p',{"class":"_2sc7ZR"})[1].text
                    final["Sno"] = count
                    count += 1
                except:
                    final["time"]  = "Not known"
                try:
                    final["name"]  = rev.find_all('div',{"class":"row _3n8db9"})[0].div.p.text
                except:
                    final["name"] = "No name"
                try:
                    final["rating"] = rev.div.div.text

                except:
                    final["rating"] = "No rating"
                try:
                    final["commentHead"] = rev.div.p.text
                except:
                    final["commentHead"] = "No heading"

                try:
                    final["comment"] = rev.find_all('div',{"class":"row"})[1].div.div.div.text
                except:
                    final["comment"] = "No comment"
                all_review.append(final)

            if(len(all_review)==0):
                return render_template('error.html')
            return render_template('results.html', all_review = all_review,title1 = searchString)

        except:
            pass
    return render_template('error.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001)