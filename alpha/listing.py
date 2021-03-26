#Gem project.
#March 2021
#Rebecca, Christine, Natalie, Fatima

import cs304dbi as dbi

#For the time being, there is one seller and her ID is:
sellerID = "rarango"
#insert into person(name, email, password) values('Rebecca', 'rarango@wellesley.edu', 'sdfd');
#inserting manually in terminal


#Retreives the id of the last inserted item.
# def getLastInsertID(conn):
#     curs = dbi.dict_cursor(conn)
#     curs.execute('''select last_insert_id()''')
#     itemID = curs.fetchone()
#     return itemID['last_insert_id()']
def insert_listing(conn,name,category,free,description,condition,price,sellmode):
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
    #For now, image not implemented. Using hardcoded image for the draft.
    curs.execute('''
        insert into item(item_name,seller_id,category,free,status,item_condition,
                        item_description,price, sellmode)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        [name,sellerID,category,free,status,condition,description,price,sellmode]) 
    conn.commit()
    curs.execute('''select last_insert_id()''')
    itemID = curs.fetchone()
    return itemID['last_insert_id()']

#Update a listing.
def update(conn,item_identifier,name,category,free,description,condition,price,sellmode):
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
                update item set item_name=%s,category=%s,free=%s,item_description=%s,item_condition=%s,price=%s,sellmode=%s
                where item_id=%s''',
                [name,category,free,description,condition,price,sellmode,item_identifier])
    conn.commit()
    result = get_listing(conn,item_identifier)
    return result

#Delete listing.
def delete(conn,item_identifier):
    '''
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
            delete from item
            where item_id = %s''',
            [itemID])
    conn.commit()
    result = get_listing(conn,item_identifier)
    if result == None:
        deleted = True
    else:
        deleted = False
    return deleted


#Retrieve all listings that are not marked as Sold.
def get_listings(conn): 
    '''
       Takes an database connection. 
       Retrieves all of the listings in the item table that 
       are marked as "Still Available". 
       Returns a list of dictionaries that contain all of the 
       information for those items.
    '''
    curs = dbi.dict_cursor(conn)
    sql  = '''select  * from item where status <> 'Sold' '''
    curs.execute(sql)
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

#Testing.
if __name__ == '__main__':
    dbi.cache_cnf()  
    dbi.use('gem_db')
    conn = dbi.connect()
    #result = getListing(conn,5)
    #result = getListings(conn)
    #result = insertListing(conn,"shirt","Clothing",False,"red","Brand New","10.50","For Sale")
    #result = insertListing(conn,"shirt","red")
    #result = getListings(conn)
    #result = getListing(conn,1)
    #result = update(conn,1,"Dress","Clothing",False,"Pink",'Brand New',12.12,'For Sale,For Rent')
    result = delete(conn,34)
    print(result) 




    