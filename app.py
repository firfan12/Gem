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
#Render Form Template
@app.route("/")
def listingForm():
    return render_template("listingForm.html")

#Form Result Function
@app.route("/listing/",methods=['POST','GET'])
def listingReturn():
    conn = dbi.connect()
    if request.method == 'POST':
        nameInput = request.form['name']
        descriptionInput = request.form['description']
        template = '''<h1>Here's what we got from you! - only description for now</h1>
            <p>Name: {nameInput1}</p>
             <p>Description: {descriptionInput1}</p>
           '''
        page = template.format(nameInput1=nameInput, descriptionInput1=descriptionInput)
        #insert item description
        listing.insertListing(conn,nameInput,descriptionInput)
        return page


#Redirect Function, possibly omit
@app.route("/feed/")
def feed():
    conn = dbi.connect()
    results =  listing.getListings(conn)
    # price = results['price']
    # name = results['item_name']
    # image = results['item_name']
    return render_template("listingFeed.html", listings = results)



#Redirect Function, possibly omit
@app.route("/item/<item_identifier>")
def itemPage(item_identifier):
    conn = dbi.connect()
    item = getListing(conn, item_identifier)
    return render_template("listingPage.html", listing = item)
    


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