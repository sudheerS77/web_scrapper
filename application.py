from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
#from urllib.request import urlopen as uReq
import urllib.request
import logging

logging.basicConfig(filename="logging.log", level=logging.INFO)

application = Flask(__name__) #initializing flask app
app = application

@app.route('/', methods=['GET']) #Homepage Route
@cross_origin()
def homePage():
    return render_template('index.html')


@app.route("/review", methods=['POST', "GET"])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipcart_url = "https://www.flipkart.com/search?q="+searchString
            uclient = urllib.request.urlopen(flipcart_url)
            flipkart_page = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkart_page, "html.parser")   
            products_cards = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del products_cards[0:3]
            product_card = products_cards[0]
            product_link = "https://www.flipkart.com"+product_card.div.div.div.a['href']
            product_req = urllib.request.urlopen(product_link)
            product_req.encoding = 'utf-8'
            product_html = bs(product_req, 'html.parser')
            product_comments_cards = product_html.find_all("div", { "class": "_16PBlm"})
            n = len(product_comments_cards)            

            file_name = searchString + '.csv'
            fw = open(file_name, "w")
            headers = "Product, Customers, Rating, Heading, comment \n"
            fw.write(headers)
            reviews = []
            for comment in product_comments_cards:
                try:
                    name = comment.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except Exception as e:
                    name = 'No Name'
                    logging.info(e)
                
                try:
                    rating = comment.div.div.div.div.text
                except Exception as e:
                    rating = "No Rating"
                    logging.info(e)
                
                try:
                    # commentHead.encode(encoding='utf-8')
                    commentHead = comment.div.div.div.p.text
                except Exception as e:
                    commentHead = 'No Comment Heading'
                    logging.info(e)

                try:
                    comtag = comment.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)                             
                mydict = {
                    "Product": searchString,
                    "Name": name,
                    "Rating": rating,
                    "CommentHead": commentHead,
                    "Comment": custComment
                }
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        
        except Exception as e:
            logging.info(e)
            return 'Something is wrong'
    else:
        return render_template('index.html')





if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)