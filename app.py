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
            searchString = request.form['content'].replace(" ","-")
            searchString = searchString.replace("(","")
            searchString = searchString.replace(")", "")

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = urlopen(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()
            print(flipkart_url)
            flipkart_html = bs(flipkart_page,'html.parser')
            for iter in range(10):
                try:
                    bigbox1 = flipkart_html.findAll('a', {"class":"_2rpwqI"})
                    if(len(bigbox1)!=0):
                        box = bigbox1[iter]
                        productLink = "https://www.flipkart.com" + box['href']
                        print(productLink)
                    else:
                        bigbox2 = flipkart_html.findAll('a', {"class": "_2UzuFa"})
                        if(len(bigbox2)!=0):
                            box = bigbox2[iter]
                            productLink = "https://www.flipkart.com" + box['href']
                            print(productLink)
                        else:
                            bigbox3 = flipkart_html.findAll('a', {"class": "_1fQZEK"})
                            box = bigbox3[iter]
                            productLink = "https://www.flipkart.com" + box['href']
                            print(productLink)
                except Exception as e:
                    print(e)

                prodRes = requests.get(productLink)
                prodHtml = bs(prodRes.text,'html.parser')
                try:
                    prodname = prodHtml.findAll('span',{'class':"G6XhRU"})[0].text
                except:
                    try:
                        prodname = prodHtml.findAll('span', {'class': "B_NuCI"})[0].text
                    except:
                        prodname=''
                review_box = prodHtml.findAll('div',{'class':"col _2wzgFH"})
                if(len(review_box)==0):
                    review_box = prodHtml.findAll('div', {'class': "col _2wzgFH _1QgsS5"})
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
                if(len(all_review)!=0):
                    break
            if(len(all_review)!=0):
                empty = 0
            else:
                empty=1
            return render_template('results.html', all_review = all_review,title1 = searchString,prodname =prodname ,empty = empty)

        except Exception as e:
            print(e)
            pass
    return render_template('error.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001)
