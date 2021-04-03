#Gem project.
#March 2021
#Rebecca, Christine, Natalie, Fatima

import cs304dbi as dbi
import os 


def insert_listing(conn,name,seller_id,category,free,description,condition,price,sellmode,image):
    '''
       Takes a database connection, item name (str), item categories (str), 
       if the item is free (boolean), item description (str), 
       item condition (str), item price (int), and if the item is 
       for sell/rent/trade (str). 
       Inserts all of the information into the item table in the database.
       Returns the ID of that item, as IDs are autoincremented.
    '''
    status = 'Still Available'
    curs = dbi.dict_cursor(conn)
    
    curs.execute('''
        insert into item(item_name,seller_id,category,free,status,item_condition,item_description,
                        price,sellmode,image)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        [name,seller_id,category,free,status,condition,description,price,sellmode,image]) 
    conn.commit()
    curs.execute('''select last_insert_id()''')
    itemID = curs.fetchone()
    return itemID['last_insert_id()']

#Update a listing.
def update(conn,item_identifier,status,name,category,free,description,condition,price,sellmode):
    '''
        Takes a database connection, the item ID (int), item name (str), 
        item categories (str), if the item is free (boolean), 
        item description (str), item condition (str), item price (int), 
        if the item is for sell/rent/trade (str).
        Updates the values of the specified item in item table.
        Returns the a dictionary with all of the item's updated information.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
                update item set item_name=%s,status=%s,category=%s,free=%s,item_description=%s,
                item_condition=%s,price=%s,sellmode=%s
                where item_id=%s''',
                [name,status,category,free,description,condition,price,sellmode,item_identifier])
    conn.commit()
    result = get_listing(conn,item_identifier)
    return result

#Delete listing.
def delete(conn,item_identifier):
    '''
        Deletes an item from the database as per the user's request.
        Different from setting an item to 'Awaiting Pickup' or 'Sold'.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
            delete from item
            where item_id = %s''',
            [item_identifier])
    conn.commit()
    result = get_listing(conn,item_identifier)
    if result == None:
        deleted = True
    else:
        deleted = False
    return deleted



#Retrieve items that current user favorited
def get_favorites(conn, username): 
    '''
       Retrieve items that current user favorited.
    '''
    curs = dbi.dict_cursor(conn)
    sql  = '''select  * from favorites where buyer_id = %s'''
    val = [username]
    
    curs.execute(sql, val)
    results = curs.fetchall()
    return results


#Retrieve the listing corresponding to a given item id.
def get_listing(conn, item_identifier): 
    '''
       Takes a database connection and ID for a particular item in a table. 
       Retrieves all the information for that item from the item table.
       Returns a single dictionary with the item information.
    '''
    curs = dbi.dict_cursor(conn)
    sql  = '''select  * from item where item_id = %s '''
    val = [item_identifier]
    curs.execute(sql, val)
    results = curs.fetchone()
    return results


#Renders a page will all listings stated as "Still Available" in 
#sorted order, cheapest to most expensive
def get_listings_by_price(conn, order): 
    '''
       Takes an database connection. 
       Retrieves all of the listings in the item table that 
       are marked as "Still Available" in sorted order by price. 
       Returns a list of dictionaries that contain all of the 
       information for those items.
    '''
    if order == 'cheap':
        sql = '''select  * from item where status <> 'Sold' order by price asc'''
    else:
        sql = '''select  * from item where status <> 'Sold' order by price desc'''
    curs = dbi.dict_cursor(conn)
    curs.execute(sql)
    results = curs.fetchall()
    return results
    

#Renders a page will all listings stated as "Still Available" for certain category
def get_listings_by_category(conn, category): 
    '''
       Takes an database connection. 
       Retrieves all of the listings in the item table that 
       are marked as "Still Available" by category
       Returns a list of dictionaries that contain all of the 
       information for those items.
    '''
    curs = dbi.dict_cursor(conn)
    sql  = '''select  * from item where status <> 'Sold' and category like %s ''' 
    val = ["%" + category + "%" ]
    curs.execute(sql, val)
    results = curs.fetchall()
    return results


#Renders a page will all listings stated as "Still Available" by their timestamp
#i.e. either newest to oldest, or newest to oldest
def get_listings_by_timestamp(conn, timestamp): 
    '''
       Takes an database connection. 
       Retrieves all of the listings in the item table that 
       are marked as "Still Available" by timestamp
       Returns a list of dictionaries that contain all of the 
       information for those items, ordered by when they were added to the db.
    '''
    curs = dbi.dict_cursor(conn)
    if timestamp == "newest":
        sql  = '''select  * from item where status <> 'Sold' order by timestamp desc'''
    elif timestamp == "oldest":
        sql = '''select  * from item where status <> 'Sold' order by timestamp asc'''
    curs.execute(sql)
    results = curs.fetchall()
    return results



    
#Get listings for a particular seller.
def get_my_listings(conn, username):
    '''
        Takes a database connection and the username of the current user.
        Retrieves all listings from the item table created by the user.
        Returns all information in a list of dictionaries, each
        representing a listing.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
            select * from item where seller_id = %s''',
            [username])
    results = curs.fetchall()
    return results

def do_files(dirname, conn, func):
    '''iterates over all files in the given directory (e.g. 'uploads'),
invoking function on conn, the full pathname, the filename and the
digits before the dot (e.g. 123.jpq).

    '''
    for name in os.listdir(dirname):
        path = os.path.join(dirname, name)
        if os.path.isfile(path):
            # note that we are reading a *binary* file not text
            with open(path,'rb') as f:
                print('{} of size {}'
                      .format(path,os.fstat(f.fileno()).st_size))
            '''nm,ext = name.split('.')'''
            '''if nm.isdigit():
                func(conn, path, name, seller_id)'''
    
def insert_picfile(conn, path, filename, seller_id):
    '''Insert name into the picfile table under key nm.'''
    curs = dbi.cursor(conn)
    try:
        curs.execute('''insert into uploads(seller_id,filename) values (%s,%s)
                   on duplicate key update filename = %s''',
                     [seller_id,filename,filename])
        conn.commit()
    except Exception as err:
        print('Exception on insert of {}: {}'.format(name, repr(err)))

#Testing.
if __name__ == '__main__':
    dbi.cache_cnf()  
    dbi.use('gem_db')
    conn = dbi.connect()
  




