from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import mongoDBCon as mongoDB

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            conStatus, dbConn = mongoDB.getMongoDB('scrapping')
            resultSet = []
            if conStatus == 1:
                colStatus, collName = mongoDB.getDBCollection(dbConn,'DataHeader')
                if colStatus == 1:
                    try:
                        dbresultSet = collName.find({"SearchStr":searchString})
                    except:
                        return 'something is wrong'
                else:
                    return 'Database collection connection Error'
            else:
                return 'Database connection Error'

            if dbresultSet.count() > 0 :
                return render_template('results.html', reviews=dbresultSet)  # show the results to user
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString
                uClient = uReq(flipkart_url)
                flipkartPage = uClient.read()
                uClient.close()
                flipkart_html = bs(flipkartPage, "html.parser")

                #bigboxes = flipkart_html.find('div',{'class':"_1YokD2 _3Mn1Gg"}).findAll("div", {"class": "_1AtVbE col-12-12"})
                bigboxes = flipkart_html.findAll("div",{"class":"_1AtVbE col-12-12"})
                del bigboxes[0:3]
                for n in range(len(bigboxes)):
                    box = bigboxes[n]
                    productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                    prodRes = requests.get(productLink)
                    prodRes.encoding='utf-8'
                    prod_html = bs(prodRes.text, "html.parser")
                    print(prod_html)

                    # Get Product and Price details
                    try:
                        prodName = prod_html.find('span', {'class': "B_NuCI"}).text
                    except:
                        prodName = 'NA'
                        pass
                    try:
                        prodRating = prod_html.find('div',{'class':"_3LWZlK"}).text
                    except:
                        prodRating = 'NA'
                        pass
                    try:
                        prodRatings = prod_html.find('span',{'class':"_2_R_DZ"}).span.span.text
                    except:
                        prodRatings = 'NA'
                        pass
                    try:
                        prodReviews = prod_html.find('span',{'class':"_13vcmD"}).next_element.next_element.text
                    except:
                        prodReviews = 'NA'
                        pass
                    try:
                        prodRevRatings = prodRatings + " & " + prodReviews
                    except:
                        prodRevRatings = 'NA'
                        pass
                    try:
                        prodExtraOff = prod_html.find('div',{'class':"_1V_ZGU"}).span.text
                    except:
                        prodExtraOff = 'NA'
                        pass
                    try:
                        prodPriceAmount = prod_html.find('div',{'class':"_30jeq3 _16Jk6d"}).text
                    except:
                        prodPriceAmount = 'NA'
                        pass
                    try:
                        prodPriceDisc = prod_html.find('div',{'class':"_3I9_wc _2p6lqe"}).text
                    except:
                        prodPriceDisc = 'NA'
                        pass
                    try:
                        prodPriceDiscPer = prod_html.find('div',{'class':"_3Ay6Sb _31Dcoz"}).span.text
                    except:
                        prodPriceDiscPer = 'NA'
                        pass
                    try:
                        prodPrice = prodPriceAmount +" After Discount of "+prodPriceDiscPer+" on actual amount "+prodPriceDisc
                    except:
                        prodPrice = 'NA'
                        pass


                    prodOffers = ""
                    prodBrandWar = ""
                    prodAvalColor = ""
                    prodAvalStorage = ""
                    prodDelivery = ""
                    prodHigPayOpt = ""
                    prodSeller = ""
                    prodDesc = ""
                    prodAddFeature = ""
                    prodSpecAtt = ""
                    prodSpec = ""

                    # Get Informative elements
                    infoElementsTags = prod_html.find('div',{'class':"_1YokD2 _3Mn1Gg col-8-12"}).findAll('div',{'class':"_1AtVbE col-12-12"})

                    for i in range(len(infoElementsTags)):

                        try:
                            prodOffers = "* "+infoElementsTags[i].find('div',{'class':"rd9nIL"}).text+" * \n"
                            try:
                                # Get Product offers.
                                prodOffElements = prod_html.findAll("span",{'class':"_3j4Zjq row"})
                                try:
                                    for j in range(len(prodOffElements)):
                                        try:
                                            prodOffers = prodOffers + prodOffElements[j].find('li',{'class':"_16eBzU col"}).findNext('span').text + " - "
                                        except:
                                            pass
                                        try:
                                            prodOffers = prodOffers + prodOffElements[j].find('span',{'class':"u8dYXW"}).findNext('span').text + "\n"
                                        except:
                                            pass
                                except:
                                    pass
                            except:
                                pass
                        except:
                            pass
                        try:
                            # Additional product offers
                            # Get Product offers.
                            prodOffElements = infoElementsTags[i].findAll("div",{'class':"_2CxnBI"})
                            try:
                                for j in range(len(prodOffElements)):
                                    try:
                                        prodOffers = prodOffers + prodOffElements[j].findNext('div').text + " - "
                                    except:
                                        pass
                                    try:
                                        prodOffers = prodOffers + prodOffElements[j].findNext('div').findNext('div').text + "\n"
                                    except:
                                        pass
                            except:
                                pass
                        except:
                            pass

                        try:
                            # Get available warranty
                            prodBrandWar = infoElementsTags[i].find("div",{'class':"_352bdz"}).text
                        except:
                            pass

                        try:
                            # Get available Color & Storage
                            prodAvalColSto = infoElementsTags[i].findAll("div",{'class':"ffYZ17 col col-12-12"})

                            for j in range(len(prodAvalColSto)):
                                try:
                                    clr = prodAvalColSto[j].find("span",{'id':"Color"})
                                    try:
                                        prodAvalClSt = prodAvalColSto[j].findAll("div",{'class', "_3Oikkn _3_ezix _2KarXJ"})
                                        for k in range(len(prodAvalClSt)):
                                            try:
                                                prodAvalColor = prodAvalColor + prodAvalClSt[k].text + ", "
                                            except:
                                                pass
                                    except:
                                        pass
                                except:
                                    try:
                                        stg = prodAvalColSto[j].find("span",{'id':"Storage"})
                                        try:
                                            prodAvalClSt = prodAvalColSto[j].findAll("div",{'class', "_3Oikkn _3_ezix _2KarXJ"})
                                            for k in range(len(prodAvalClSt)):
                                                try:
                                                    prodAvalStorage = prodAvalStorage + prodAvalClSt[k].text + ", "
                                                except:
                                                    pass
                                        except:
                                            pass
                                    except:
                                        pass
                        except:
                            pass

                        try:
                            # Get Usuall delivery time
                            prodDelivery = infoElementsTags[i].find("div",{'class':"_3XINqE"}).text
                            prodDelivery = prodDelivery + " "+ infoElementsTags[i].find("span",{'class':"_1TPvTK"}).text
                        except:
                            pass

                    # Product Highlights
                    try:
                        prodHigPayOpts = prod_html.findAll('div',{'class':"_1AtVbE col-6-12"})
                        for i in range(len(prodHigPayOpts)):
                            try:
                                prodHigPayOpt = prodHigPayOpt + prodHigPayOpts[i].find('div',{'class':"_3a9CI2"}).text +" \n"
                                try:
                                    prodHighlights = prodHigPayOpts[i].findAll('li',{'class':"_21Ahn-"})
                                    for j in range(len(prodHighlights)):
                                        prodHigPayOpt = prodHigPayOpt + prodHighlights[j].text + " \n"
                                except:
                                    pass
                            except:
                                # Get Easy Payment Options
                                try:
                                    prodHigPayOpt = prodHigPayOpt + prodHigPayOpts[i].find('div', {'class': "Yd8aaW"}).text + " \n"
                                    try:
                                        prodHighlights = prodHigPayOpts[i].findAll('li', {'class': "_1Ma4bX"})
                                        for j in range(len(prodHighlights)):
                                            prodHigPayOpt = prodHigPayOpt + prodHighlights[j].text + " \n"
                                    except:
                                        pass
                                except:
                                    pass
                    except:
                        pass

                    # Product Seller
                    try:
                        prodSeller = prod_html.find('div',{'class':"_1YokD2 _3Mn1Gg"}).find('div',{'id':"sellerName"}).span.span.text + " \n"
                    except:
                        pass

                    # Product Seller Condition
                    try:
                        prodSellConds = prod_html.find('div',{'class':"_1YokD2 _3Mn1Gg"}).find('ul',{'class':"_2-RJLI"}).findAll('li',{'class':"_1UNqMC"})
                        for i in range(len(prodSellConds)):
                            try:
                                prodSeller = prodSeller + prodSellConds[i].div.text + " \n"
                            except:
                                pass
                    except:
                        pass

                    # Product Description
                    try:
                        prodDesc = prod_html.find('div',{'class':"_1A1InN"}).find('div',{'class':"_1GoqrO"}).text
                    except:
                        pass

                    # Product Additional Feature Description
                    try:
                        prodAddFeaturesTag = prod_html.find('div',{'class':"_1YokD2 _3Mn1Gg"}).findAll('div',{'class':"_1AtVbE col-12-12"})
                        for i in range(len(prodAddFeaturesTag)):
                            try:
                                prodAddFeatures = prodAddFeaturesTag[i].findAll('div',{'class':"_2k6Cpt"})
                                for j in range(len(prodAddFeatures)):
                                    # Get header title
                                    try:
                                        prodAddFeature = prodAddFeature + prodAddFeatures[j].find('div',{'class':"_3qWObK"}).text +" - \n"
                                    except:
                                        pass

                                    # Get description
                                    try:
                                        prodAddFeature = prodAddFeature + "\t" + prodAddFeatures[j].find('div',{'class':"_3zQntF"}).p.text +" \n"
                                    except:
                                        pass
                            except:
                                pass

                            '''
                            # Product specifications
                            try:
                                #prodSpecs = prodAddFeaturesTag[i].findAll('div',{'class':"flxcaE"})
                                prodSpecs = prodAddFeaturesTag[i].findAll('div',{'class':"_3k-BhJ"})
                                for j in range(len(prodSpecs)):
                                    try:
                                        prodSpec = prodSpec + prodSpecs[j].find('div',{'class':"flxcaE"}).text +" - "
                                        try:
                                            prodSpecAtts = prodSpecs[j].findAll('tr',{'class':"_1s_Smc row"})
                                            for k in range(len(prodSpecAtts)):
                                                try:
                                                    prodSpecAtt = prodSpecAtt + prodSpecAtts[k].find('td',{'class':"_1hKmbr col col-3-12"}).text +" - "
                                                    try:
                                                        prodSpecAtt = prodSpecAtt + prodSpecAtts[k].find('li',{'class':"_21lJbe"}).text + " \n"
                                                    except:
                                                        pass
                                                except:
                                                    pass
                                            prodSpec = prodSpec + prodSpecAtt +", "
                                        except:
                                            pass
                                    except:
                                        pass
                            except:
                                pass
                            '''
                    except:
                        pass

                    mydict = {"SearchStr":searchString,"ProductName":prodName,"ProductPrice":prodPrice,"ProductRating":prodRating,"Review-Ratings":prodRevRatings,"Warranty":prodBrandWar,"Offers":prodOffers,"AvailableColors":prodAvalColor,"Storage":prodAvalStorage,"DaysDelivery":prodDelivery,"PayOut":prodHigPayOpt,"Seller":prodSeller}
                    x = collName.insert_one(mydict)
                    #resultSet.append(mydict)
                return render_template('results.html', reviews = collName.find({"SearchStr":searchString}))  # showing the review to the user

        except:
            return render_template('results.html', reviews = collName.find({"SearchStr":searchString}))  # showing the review to the user
    else:
        return render_template('index.html')


if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
