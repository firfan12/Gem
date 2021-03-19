#Establish Routes for Listing Form
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
import listing
# import cs304dbi_sqlite3 as dbi

import random
#Render main page.
@app.route("/")
def index():
 return render_template("base.html")

#Render Form Template
@app.route("/listingform/")
def listingForm():
    return render_template("listingForm.html")

#Form Result Function
@app.route("/listing/",methods=['POST','GET'])
def listingReturn():
    conn = dbi.connect()
    if request.method == 'POST':
        #Retreive answers.
        name = request.form['name']
        #For now, let's just say that the item is only category 'clothing'.
        categoryClothing = request.form['category1']
        description = request.form['description']
        condition = request.form['condition']
        #No database equivalent yet for 'availablefor'.
        #availableForSell = request.form['sellmode1']
        #ffofp means "for free or for price"
        ffofp = request.form['ffofp']
        if ffofp == 'free':
            free = True
            price = None
        else: 
            free = False
            price = request.form['price']
        #Insert into DB, retreive itemID: 
        itemID = listing.insertItem(conn,name,categoryClothing,free,description,condition,price)
        print(itemID)
        #Retrieve the listed item:
        #item = listing.getListing(conn,itemID)
        return redirect(url_for('itemPage',item_identifier = itemID))


#Redirect Function, possibly omit
@app.route("/feed/")
def feed():
    conn = dbi.connect()
    results =  listing.getListings(conn)
    # price = results['price']
    # name = results['item_name']
    # image = results['item_name']
    return render_template("listingFeed.html", listings = results)


#Page for an individual item. 
@app.route("/item/<item_identifier>")
def itemPage(item_identifier):
    conn = dbi.connect()
    item = listing.getListing(conn,item_identifier)
    return render_template("item.html", listing = item)
    


if __name__ == '__main__':
    dbi.cache_cnf()  
    dbi.use('gem_db')
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)