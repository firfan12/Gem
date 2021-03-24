#Gem project.
#March 2021
#Rebecca, Christine, Natalie, Fatima

#Establish Routes for Listing Form
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
import listing  #imports helper methods
# import cs304dbi_sqlite3 as dbi
import random
import bcrypt

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

#routes users to the Gem home page
@app.route('/')
def index():
    '''
       Renders the home page.
    '''
    return render_template('main.html',page_title='Gem Home Page')


#show user's all of their favorites listings on one  page
@app.route('/favorites/')
def favorites():
    '''
       Renders favorites.
    '''
    return render_template('favorites.html',page_title='Favorite Items')


#Doesn't work, not finished implementing!
#show user's their profile. profile.html not implemented yet, 
# so this route mostly not implemented yet
@app.route('/profile/')
def profile():
    '''
       Renders the template for the profile.
    '''
    return render_template('profile.html',page_title='User Profile')

@app.route('/login/')
def login():
    '''
    Renders the template for the login page
    '''
    return render_template('login.html', page_title='Login')


#creates the feed for the user to view all listings 
#of items that are not sold
@app.route("/listings/") #methods=['POST','GET']?
def listings():
    '''
       Renders a page will all listings stated as "Still Available".
    '''
    conn = dbi.connect()
    results =  listing.getListings(conn)
    # price = results['price']
    # name = results['item_name']
    # image = results['item_name']
    return render_template("listings.html", listings = results, page_title='All listings')

#renders the page for an individual item listing
#Checks if the viewer is the buyer or seller.
#If the viewer is a seller, then display the update and delete buttons.
#If the viewer is a buyer, then 
@app.route("/item/<item_identifier>") #methods=['POST','GET']?
def itemPage(item_identifier):
    '''
       Renders a page for a single item.
       If the view is a seller, displays an update and delete button.
       If the viewer is a buyer, then displays a "contact" button to contact the seller.
    '''
    conn = dbi.connect()
    item = listing.getListing(conn, item_identifier)
    return render_template("item_page.html", listing = item, page_title='One listing')


#renders the page where one can create a listing
@app.route("/createlisting/") #methods=['POST','GET']?
def createListing():
    '''
       Renders the form to create a listing.
    '''
    return render_template("listing_form.html", page_title='Create a listing',update=False)

@app.route("/updatelisting/<int:itemID>")
def updateListing(itemID):
    '''
        Renders the form to update a listing.
    '''
    conn = dbi.connect()
    listingForUpdate = listing.getListing(conn,itemID)
    return render_template("update.html",listing = listingForUpdate,page_title="Update Listing")
    #listing = listing.getListing(itemID)
    #return render_template("update.html",listing = listing,page_title="Update Listing")


#Processes users query for a certain item.
#Handles queries differently based on whether the query has any matches in the database.
@app.route('/search/') #methods=['POST','GET']?
def query():
    '''
       Renders search.
    '''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = request.args['search']
   
    #will include searching tags in the beta if have time 
    # get all listings in db that has this query as part of its name
    sql = '''select * from item where item_name like %s 
    or category like %s or item_description like %s''' #joining bc dn want duplicates
    vals = ['%' + query + '%', '%' + query + '%', '%' + query + '%'] 
    curs.execute(sql, vals)
    results = curs.fetchall()
    
    #process query based on how many items from the database matched the query:
    if len(results) == 0:  
        flash("Sorry, no items were found!")
        #fig. out how to remove other flashed messages when flashing this one!
        #i.e. it still said 21 listings found when tried to find a different listing
        return redirect(request.referrer)
        #return render_template('no_query_result.html', page_title ='No Query Results')
                                # message = "Sorry, no items were found with that name")                     
    elif len(results) == 1:  #works
        item_id = results[0].get("item_id")
        flash("Search results: one item found") 
        return redirect(url_for('itemPage', item_identifier = item_id))
    elif len(results) > 1:
        flash("Search results: {number_items} item found".format(number_items = len(results)))
        return render_template('listings.html', listings = results, page_title ='Listings Found')

 
#After a user submits a listing to be posted, this route
#returns to them the result of their successful listing
#and tells them that their listing was posted.
@app.route("/listing/",methods=['POST','GET'])
def listingReturn():
    '''
        This route displays the result of the item, whether it has been inserted or updated.
    '''
    conn = dbi.connect()
    if request.method == 'POST':
        #Retreive all submitted listing information.
        name = request.form['name']
        #Get list of categories.
        categories = (',').join(request.form.getlist('category'))       
        description = request.form['description']
        condition = request.form['condition']
        price = request.form['price']
        if (price == 0): 
            free = True
        else:
            free = False
        #Get list of sellmodes.
        sellmode = (',').join(request.form.getlist('sellmode'))
        #Insert into DB, retreive itemID: 
       
        itemID = listing.insertListing(conn,name,categories,free, description, 
                condition,price,sellmode) 
        print(itemID)
        flash("Congrats! Your item is now listed for sale")
        return redirect(url_for('itemPage',item_identifier = itemID))      

#Does some initializing, including saying what database to use
@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use =  'gem_db'
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))  #for testing purposes


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