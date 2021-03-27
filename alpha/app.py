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

@app.route('/join/', methods=["POST", "GET"])
def join():
    if request.method == 'GET':
        return render_template('register.html', page_title='Join Gem')
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            passwd1 = request.form['password1']
            passwd2 = request.form['password2']
            if passwd1 != passwd2:
                flash('Passwords do not match. Please try again.')
                return redirect( url_for('register'))
            hashed = bcrypt.hashpw(passwd1.encode('utf-8'),
                                bcrypt.gensalt())
            hashed_str = hashed.decode('utf-8')
            print(passwd1, type(passwd1), hashed, hashed_str)
            conn = dbi.connect()
            curs = dbi.cursor(conn)
            try:
                curs.execute('''INSERT INTO person(email)
                                VALUES(%s)''',
                            [username])
                curs.execute('''INSERT INTO userpass(user,hashed)
                                VALUES(%s,%s)''',
                            [username, hashed_str])
                conn.commit()
            except Exception as err:
                flash('That username is taken. Please pick a different username')
                return redirect(url_for('join'))
            curs.execute('select last_insert_id()')
            row = curs.fetchone()
            session['username'] = username
            session['logged_in'] = True
            session['visits'] = 1
            return redirect(url_for('profile'))
            #return redirect( url_for('user', username=username) )
        except Exception as err:
            flash('form submission error '+str(err))
            return redirect( url_for('index') )

@app.route('/login/', methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html', page_title='Log In To Gem')   
    if request.method == 'POST':
        try:
            username = request.form['username']
            passwd = request.form['password']
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute('''SELECT hashed
                        FROM userpass
                        WHERE user = %s''',
                        [username])
            row = curs.fetchone()
            if row is None:
                # Same response as wrong password,
                # so no information about what went wrong
                flash('Login incorrect. Try again or join')
                return redirect( url_for('login'))
            hashed = row['hashed']
            print('database has hashed: {} {}'.format(hashed,type(hashed)))
            print('form supplied passwd: {} {}'.format(passwd,type(passwd)))
            hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),
                                    hashed.encode('utf-8'))
            hashed2_str = hashed2.decode('utf-8')
            print('rehash is: {} {}'.format(hashed2_str,type(hashed2_str)))
            if hashed2_str == hashed:
                print('they match!')
                flash('Successfully logged in as '+username)
                session['username'] = username
                session['logged_in'] = True
                session['visits'] = 1
                return redirect(url_for('profile'))
                #return redirect( url_for('user', username=username) )
            else:
                flash('Login incorrect. Try again or join')
                return redirect( url_for('login'))
        except Exception as err:
            flash('form submission error '+str(err))
            return redirect( url_for('index') )

@app.route('/logout/')
def logout():
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(url_for('index'))
        else:
            flash('You are not logged in. Please log in or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )


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
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            username = session['username']
            session['visits'] = 1+int(session['visits'])
            return render_template('profile.html',
                                   page_title='My App: Welcome {}'.format(username),
                                   name=username,
                                   visits=session['visits'])

        else:
            flash('You are not logged in. Please log in or join')
            return redirect( url_for('login') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('login') )

#creates the feed for the user to view all listings 
#of items that are not sold
@app.route("/listings/")
def listings():
    '''
       Renders a page will all listings stated as "Still Available".
    '''

    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            conn = dbi.connect()
            results =  listing.getListings(conn)
            return render_template("listings.html", listings = results, page_title='All listings')

        else:
            flash('You are not logged in. Please log in or join')
            return redirect( url_for('login') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('login') )

    # price = results['price']
    # name = results['item_name']
    # image = results['item_name']
#renders the page for an individual item listing
#Checks if the viewer is the buyer or seller.
#If the viewer is a seller, then display the update and delete buttons.
#If the viewer is a buyer, then 
@app.route("/item/<item_identifier>")
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
@app.route("/createlisting/")
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


#Doesn't work, not finished implementing!
#Processes users query for a certain movie or person. 
#Handles queries differently based on whether the query has any matches in the database.
@app.route('/search/')
def query():
    '''
       Renders search.
    '''
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