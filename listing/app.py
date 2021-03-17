#Establish Routes for Listing Form
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import random
#Render Form Template
@app.route("/")
def listingForm():
    return render_template("listingForm.html")

#Form Result Function
@app.route("/listingresult/",methods=['POST','GET'])
def listingReturn():
    if request.method == 'POST':
        price = request.form["price"]
        print(price)
        template = '''<h1>Here's what we got from you!</h1>
             <p>Price: {priceInput} </p>
             <p>Description:</p>
           '''
        page = template.format(priceInput = price)
        return page

#Redirect Function, possibly omit
@app.route("/listingredirect/")
def listingRedirect():
    price = request.args.get('price')
    description = request.args.get('description')
    return redirect(url_for("listingReturn", price = price, description = description))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)