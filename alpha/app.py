#File Name: app.py
#Project: Gem
#Spring 2021
#RA, CP, NR, FI

#Establish Routes for Listing Form
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify, Response)
from werkzeug.utils import secure_filename
app = Flask(__name__)


import cs304dbi as dbi
import listing  #imports helper methods
# import cs304dbi_sqlite3 as dbi
import random
import bcrypt
import logins
import sys, os, random
import imghdr




app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

#routes users to the Gem home page
@app.route('/')
def index():
    '''
       Renders the home page.
    '''
    ifLoggedIn = 'username' in session
    return render_template('main.html',page_title='Gem Home Page', loggedin = ifLoggedIn )

@app.route('/join/', methods=["POST", "GET"])
def join():
    if request.method == 'GET':
        ifLoggedIn = 'username' in session
        return render_template('register.html', page_title='Join Gem', loggedin = ifLoggedIn)
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            passwd1 = request.form['password1']
            passwd2 = request.form['password2']
            email = request.form['email']
            if passwd1 != passwd2:
                flash('Passwords do not match. Please try again.')
                return redirect( url_for('join'))
            hashed = bcrypt.hashpw(passwd1.encode('utf-8'),
                                bcrypt.gensalt())
            hashed_str = hashed.decode('utf-8')
            conn = dbi.connect()
            curs = dbi.cursor(conn)
            try:
                curs.execute('''INSERT INTO person(name,email)
                                VALUES(%s,%s)''',
                            [username, email])
                curs.execute('''INSERT INTO userpass(user,hashed)
                                VALUES(%s,%s)''',
                            [email, hashed_str])
                conn.commit()
            except Exception as err:
                flash('That username is taken. Please pick a different username{}'.format(str(err)) )
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
        ifLoggedIn = 'username' in session 
        return render_template('login.html', page_title='Log In To Gem', loggedin = ifLoggedIn)   
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
            hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),
                                    hashed.encode('utf-8'))
            hashed2_str = hashed2.decode('utf-8')
            if hashed2_str == hashed:
                flash('Successfully logged in as '+username)
                session['username'] = username
                session['logged_in'] = True
                session['visits'] = 1
                return redirect(url_for('index'))
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

@app.route('/profile/')
def profile():
    '''
       Renders the template for the profile.
    '''
    conn = dbi.connect()
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            username = session['username']
            session['visits'] = 1+int(session['visits'])
            my_listings = listing.get_my_listings(conn,username)
            ifLoggedIn = 'username' in session 
            return render_template('profile.html',
                                   page_title='Gem: Welcome {}'.format(username),
                                   name=username,
                                   visits=session['visits'],
                                   listings=my_listings, loggedin = ifLoggedIn)

        else:
            flash('You are not logged in. Please log in or join')
            return redirect( url_for('login') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

@app.route("/createlisting/",methods=['POST','GET'])
def create_listing():
    '''
       If a GET request, renders the form to create a listing.
       If a POST request, retreives information from the form,
       inserts a new listing, returns the auto-incremented ID of 
       that listing, and redirects to the item_page/<ID> url.
    '''
    conn = dbi.connect()
    if request.method == "GET":
        try:
            # don't trust the URL; it's only there for decoration
            if 'username' in session:
                results =  listing.get_listings(conn)
                ifLoggedIn = 'username' in session
                return render_template("listing_form.html", page_title='Create a listing',update=False, 
                                        loggedin = ifLoggedIn)
            else:
                flash('You are not logged in. Please log in or join')
                return redirect( url_for('login') )
        except Exception as err:
            flash('some kind of error {}'.format(str(err)))
            return redirect( url_for('login') )
    elif request.method == "POST":
        #If the seller is inserting a listing.
        if request.form['submit'] == 'insert':
            #Retrieve values from the "Insert Listing" form.
            name = request.form['name']
            categories = (',').join(request.form.getlist('category'))
            description = request.form['description']
            condition = request.form['condition']
            price = request.form['price']
            if (price == 0): 
                free = True
            else:
                free = False
            sellmode = (',').join(request.form.getlist('sellmode'))
            seller_id = session['username']
            #File Uploads:
            try:
                f = request.files['pic']
                filename = f.filename
                #ext = user_filename.split('.')[-1]
                #filename = secure_filename('{}.{}'.format(user_filename,ext))
                pathname = os.path.join(app.config['UPLOADS'],filename)
                f.save(pathname)
            except Exception as err:
                flash('Upload failed {why}'.format(why=err))
                return render_template('listing_form.html',src='')
            
            image = filename
            #Should this be outsourced to listing.py?
            curs = dbi.dict_cursor(conn)
            curs.execute('''insert into uploads(seller_id,filename) values (%s,%s)
                on duplicate key update filename = %s''',
                    [seller_id,filename,filename])
            conn.commit()
            #flash('Upload successful')
            #Insert into DB, retreive itemID.
            item_identifier = listing.insert_listing(conn,name,seller_id,categories,free,
                                description,condition,price,sellmode,image) 
            flash("Congrats! Your item is now listed for sale")
            #Redirect to itemPage URL with the item ID.
            return redirect(url_for('item_page',item_identifier = item_identifier))
        #Do I need to through an error here?
    return redirect('<p>Error</p>')  


#listings by order
@app.route("/listings/price/<order>", methods=['GET'])
def listings_by_price(order):
    '''Renders listings in a certain category, or'''
    item_categories = ('Clothing','Accessories','Dorm Essentials','Beauty',
                'School Supplies','Tech','Furniture','Textbooks','Food','Other')
    item_orderings = ('Price: Low to High', 'Price: High to Low')
    if request.method == 'GET': 
        conn = dbi.connect()
        #Get item listings for the given category
        items = listing.get_listings_by_price(conn, order)
        username = session['username']
        ifLoggedIn = 'username' in session
        return render_template("listings.html",username=username,
        listings = items, page_title='Listings by Price', categories = item_categories, 
        possible_orderings = item_orderings, loggedin = ifLoggedIn)
        


#listings by category
@app.route("/listings/category/<category>",methods=['POST','GET'])
def listings_by_category(category):
    '''
       Renders listings in  a given order by price. 
    '''
    conn = dbi.connect()
    item_categories = ('Clothing','Accessories','Dorm Essentials','Beauty',
                'School Supplies','Tech','Furniture','Textbooks','Food','Other')
    item_orderings = ('Price: Low to High', 'Price: High to Low')
    if request.method == 'GET': 
        #Get listings for the given order
        items = listing.get_listings_by_category(conn, category)
        username = session['username']
        ifLoggedIn = 'username' in session
        return render_template("listings.html",username=username,
        listings = items, page_title='Listings by Order', categories = item_categories, 
        possible_orderings = item_orderings, loggedin = ifLoggedIn)
        # price = results['price']
        # name = results['item_name']
        # image = results['item_name']

    
@app.route('/pic/<image>')
def pic(image):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    numrows = curs.execute(
        '''select filename from uploads where filename = %s''',
        [image])
    if numrows == 0:
        flash('No picture for {}'.format(filenamep))
        return redirect(url_for('index'))
    row = curs.fetchone()
    return send_from_directory(app.config['UPLOADS'],row['filename'])

    

#renders the page for an individual item listing
#Checks if the viewer is the buyer or seller.
#If the viewer is a seller, then display the update and delete buttons.
#If the viewer is a buyer, then 
@app.route("/item/<item_identifier>",methods=['POST','GET'])
def item_page(item_identifier):
    '''
       Renders a page for a single item.
       If the view is a seller, displays an update and delete button.
       If the viewer is a buyer, then displays a "contact" button to contact the seller.
    '''
    conn = dbi.connect()
    #If the request is GET.
    if request.method == 'GET': 
        #Get the database dictionary of the item given its ID.
        item = listing.get_listing(conn, item_identifier)
        username = session['username']
        ifLoggedIn = 'username' in session
        return render_template("item_page.html",username=username,listing = item, 
                                page_title='One listing', loggedin = ifLoggedIn)
    #If the request is POST.
    if request.method == "POST":
        #If the seller wishes to update their listing.
        if request.form['submit'] == 'update':
            name = request.form['name']
            categories = (',').join(request.form.getlist('category'))
            description = request.form['description']
            condition = request.form['condition']
            price = request.form['price']
            if (price == 0): 
                free = True
            else:
                free = False
            sellmode = (',').join(request.form.getlist('sellmode'))
            status = request.form['status']
            #Update the listing.
            updated_listing = listing.update(conn,item_identifier,status,name,categories,free,
                                description,condition,price,sellmode)
            username = session['username']
            flash('Your item has been updated!')
            #Re-render the item page with the correct values.
            ifLoggedIn = 'username' in session
            return render_template('item_page.html',username=username,listing=updated_listing,
                                page_title="Updated Listing", loggedin = ifLoggedIn) 
#creates the feed for the user to view all listings 
#of items that are not sold
@app.route("/listings/", methods=['POST','GET'])
def listings():
    '''
       Renders a page will all listings stated as "Still Available".
    '''
    item_categories = ('Clothing','Accessories','Dorm Essentials','Beauty',
                'School Supplies','Tech','Furniture','Textbooks','Food','Other')
    orderings = ('Price: Low to High', 'Price: High to Low')
    if request.method == 'GET':
        try:
            # don't trust the URL; it's only there for decoration
            if 'username' in session:
                conn = dbi.connect()
                results =  listing.get_listings(conn)
                ifLoggedIn = 'username' in session
                return render_template("listings.html", listings = results, page_title='All listings', 
                categories = item_categories, possible_orderings = orderings, loggedin = ifLoggedIn)
            else:
                flash('You are not logged in. Please log in or join')
                return redirect( url_for('login') )
        except Exception as err:
            flash('some kind of error '+str(err))
    elif request.method == 'POST':
        action = request.form['submit-btn']
        if action == "Choose":
            selected_category = request.form.get("menu-category")
            return redirect(url_for('listings_by_category', category = selected_category))
        elif action == "Select":
            selected_order = request.form['menu-order']
            if selected_order == orderings[0]:
                order = "cheap"     
            elif selected_order == orderings[1]:
                order = "expensive"
            return redirect(url_for('listings_by_price', order = order))



    # price = results['price']
    # name = results['item_name']
    # image = results['item_name']

@app.route("/updatelisting/<int:item_identifier>")
def update_listing(item_identifier):
    '''
        Retreives information from database about the listing to be updated.
        Renders the form to update a listing.
    '''
    conn = dbi.connect()
    item = listing.get_listing(conn,item_identifier)
    all_categories = ('Clothing','Accessories','Dorm Essentials','Beauty',
                        'School Supplies','Tech','Furniture','Textbooks','Food','Other')
    all_conditions = ('Brand New','Gently Used','Well Loved')
    all_sellmodes = ('For Sale','For Rent','For Trade')
    all_statuses = ('Still Available','Awaiting Pickup','Sold')
    ifLoggedIn = 'username' in session
    return render_template("update.html",
                            listing = item,
                            page_title="Update Listing",  
                            loggedin = ifLoggedIn,
                            all_categories=all_categories,
                            all_conditions=all_conditions,
                            all_sellmodes=all_sellmodes,
                            all_statuses=all_statuses)

@app.route("/deletelisting/<int:item_identifier>",methods=['POST','GET'])
def delete_listing(item_identifier):
    '''
        Renders a page that asks the user if they are sure they want to delete this listing.
        Different from setting status to 'Awaiting Pickup' or 'Sold'.
    '''
    conn = dbi.connect()
    if request.method == 'GET':
        listing_delete = listing.get_listing(conn,item_identifier)
        ifLoggedIn = 'username' in session
        return render_template("delete.html", listing = listing_delete, loggedin = ifLoggedIn )
    elif request.method == 'POST':
        deleted_listing = listing.delete(conn,item_identifier)
        flash('Your listing was successfully deleted.')
        return redirect(url_for('index'))

#Processes users query for a certain item.
#Handles queries differently based on whether the query has any matches in the database.
@app.route('/search/') #methods=['POST','GET']?
def query():
    '''
       Renders search.
    '''
    item_categories = ('Clothing','Accessories','Dorm Essentials','Beauty',
                'School Supplies','Tech','Furniture','Textbooks','Food','Other')
    item_orderings = ('Price: Low to High', 'Price: High to Low')
    try:
        if 'username' in session:
            username = session['username']
            session['visits'] = 1+int(session['visits'])
    
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            query = request.args['search']
        
            #will include searching tags in the beta if have time 
            # get all listings in db that has this query as part of its name, description, 
            #or category
            sql = '''select * from item where item_name like %s 
            or category like %s or item_description like %s''' #joining because don't want duplicates
            vals = ['%' + query + '%', '%' + query + '%', '%' + query + '%'] 
            curs.execute(sql, vals)
            results = curs.fetchall()
            
            #process query based on how many items from the database matched the query:
            if len(results) == 0:  
                flash("Sorry, no items were found!") #
                return redirect(request.referrer)                 
            elif len(results) == 1:  
                item_id = results[0].get("item_id")
                flash("Search results: one item found") 
                return redirect(url_for('item_page', item_identifier = item_id))
            elif len(results) > 1:
                flash("Search results: {number_items} item found".format(number_items = len(results)))
                ifLoggedIn = 'username' in session 
                return render_template('listings.html', listings = results, 
                                        page_title ='Listings Found',
                                     categories = item_categories, 
                                     possible_orderings = item_orderings, 
                                     loggedin = ifLoggedIn )
        else:
            flash('You are not logged in. Please log in or join')
            return redirect( url_for('login') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('login') )

#Renders page with feed showing the user all their favorited items
@app.route("/favorites/") 
def favorites():
    '''
       Renders page with feed showing the user all their favorited items
    '''
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            conn = dbi.connect()
            results =  listing.get_favorites(conn, 'username')
            # print("Here is the session username:")
            # print(session['username'])
            ifLoggedIn = 'username' in session
            return render_template("favorites.html", listings = results, page_title='Favorite items', 
                                    loggedin = ifLoggedIn)
        else:
            flash('You are not logged in. Please log in or join')
            return redirect( url_for('login') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('login') )

#Initialize
@app.before_first_request
def init_db():
    dbi.cache_cnf()
    db_to_use =  'gem_db'
    dbi.use(db_to_use)

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