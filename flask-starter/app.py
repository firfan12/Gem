from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import listing  #helper methods

import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('main.html',title='Hello')

@app.route('/greet/', methods=["GET", "POST"])
def greet():
    if request.method == 'GET':
        return render_template('greet.html', title='Customized Greeting')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )

@app.route('/formecho/', methods=['GET','POST'])
def formecho():
    if request.method == 'GET':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.args)
    elif request.method == 'POST':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.form)
    else:
        # maybe PUT?
        return render_template('form_data.html',
                               method=request.method,
                               form_data={})

@app.route('/testform/')
def testform():
    # these forms go to the formecho route
    return render_template('testform.html')

#show user's favorites
@app.route('/favorites/')
def favorites():
    return render_template('favorites.html',title='Favorite Items')


#show user's favorites
@app.route('/profile/')
def profile():
    return render_template('profile.html',title='User Profile')


#created feed
@app.route("/listings/")
def listings():
    conn = dbi.connect()
    results =  listing.getListings(conn)
    # price = results['price']
    # name = results['item_name']
    # image = results['item_name']
    return render_template("listings.html", listings = results)



#Redirect Function, possibly omit
@app.route("/item/<item_identifier>")
def itemPage(item_identifier):
    conn = dbi.connect()
    item = listing.getListing(conn, item_identifier)
    return render_template("itemPage.html", listing = item)
    

#page for creating a listing
@app.route("/listingform")
def listingForm():
    return render_template("listingForm.html")


#Processes users query for a certain movie or person. 
#Handles queries differently based on whether the query has any matches in the database.
@app.route('/search/')
def query():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = request.form['search']
   
    # get all listings in db that has this query as part of its name
    sql = '''select * from item where item_name like  %s'''
    vals = ['%' + query + '%']
    curs.execute(sql, vals)
    results = curs.fetchall()
    #process query based on how items from the database matched the query:
    if len(results) == 0:  
        return render_template('no_query_result.html', page_title ='No Query Results', 
                                message = "Sorry, no items were found with that name")  
    elif len(results) == 1: 
        item_id = results[0].get("item_id")
        return redirect(url_for('itemPage', item_identifier = item_id))
    elif len(results) > 1:
        return render_template('listings.html', page_title ='Listings Found',listings = results)

#Processes users query for a certain movie or person. 
#Handles queries differently based on whether the query has any matches in the database.
#https://stackoverflow.com/questions/19794695/flask-python-buttons 
def main_page_buttons():
    if request.method == 'POST':
        if request.form['submit_button'] == "buy":
            pass # do something
        elif request.form['submit_button'] == "sell":
            pass # do something else
        else:
            pass # unknown
    elif request.method == 'GET':
        return render_template('contact.html', form=form)

   

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

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use =  'gem_db'
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))

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
