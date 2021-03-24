#Gem project.
#March 2021
#Rebecca, Christine, Natalie, Fatima

#Establish Routes for Listing Form
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)


import cs304dbi as dbi
import listing  #imports helper methods
# import cs304dbi_sqlite3 as dbi
import random


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
    return render_template('main.html', page_title='Gem Home Page')


#Doesn't work yet; The favorites route and favorites.html is not implemented for 
#the draft version.
#shows users all of the listings that they favorited on one page
@app.route('/favorites/')
def favorites():
    return render_template('favorites.html', page_title='Favorite Items')


#Doesn't work yet; The profile route and profile.html is not implemented 
#for the draft version.
#Displays the user's profile. 
@app.route('/profile/')
def profile():
    return render_template('profile.html', page_title='User Profile')


#Shows the feed of all item listings that are not marked as sold
@app.route("/listings/")
def listings():
    conn = dbi.connect()
    results =  listing.getListings(conn)
    # price = results['price']
    # name = results['item_name']
    # image = results['item_name']
    return render_template("listings.html", listings = results, page_title='All listings')


#Renders the page for an individual item listing
@app.route("/item/<item_identifier>")
def itemPage(item_identifier):
    conn = dbi.connect()
    item = listing.getListing(conn, item_identifier)
    return render_template("item_page.html", listing = item, page_title='A Item listing')



#Renders the page where one can create a new listing.
@app.route("/listingform/")
def listingForm():
    return render_template("listing_form.html", page_title ='Create a listing')



#The search bar  and this route do not work yet, not implemented for the draft version!
#Processes users search for a certain item.
#Handles queries differently based on whether the query has any matches in the database.
@app.route('/search/')
def query():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = request.args['search']
   
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



#After a user submits a listing to be posted, this route
#returns to them the result of their successful listing
#and flashes a message to them stating that their listing was posted.
@app.route("/listing/",methods=['POST','GET'])
def listingReturn():
    conn = dbi.connect()
    if request.method == 'POST':
        #Retreive all submitted listing information.
        name = request.form['name']
        #you can select more than one category.
        categoryClothing = (',').join(request.form.getlist('category'))
        # print("========================================" + str(categoryClothing))
        description = request.form['description']
        condition = request.form['condition']
        price = request.form['price']
        if (price == 0): 
            free = True 
        else:
            free = False
        # sell mode only  works for ONE option at the moment
        #We have not implemented it yet such that one 
        #can select more than one mode of selling (trade, rent, buy).
        availableForMode = (',').join(request.form.getlist('sellmode'))
        # print("========================================" + str(availableForMode))
        
        #Insert into DB, retreive itemID for testing purposes:
        itemID = listing.insertListing(conn,name,categoryClothing,free, description, 
                condition,price,availableForMode) 
        print(itemID)

        #Retrieve the listed item:
        #item = listing.getListing(conn,itemID)
        flash("Congrats! Your item is now listed for sale")
        return redirect(url_for('itemPage',item_identifier = itemID))



#Does some initializing, including saying what database to use
@app.before_first_request
def init_db():
    dbi.cache_cnf()
    db_to_use =  'gem_db' #our team database
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