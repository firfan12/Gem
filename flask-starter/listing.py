import cs304dbi as dbi

#For the time being, there is one seller and her ID is:
seller_id = "rarango@wellesley.edu"

#Insert new listing; returns the auto-incremented ID of that listing.
#Draft:
def insertListing(conn,name,category,free,description,condition,price):
    status = 'Still Available'
    curs = dbi.dict_cursor(conn)
    #For now, no image.
    curs.execute('''
        insert into item(item_name,seller_id,category,free,status,item_condition,item_description,price)
        values (%s,%s,%s,%s,%s,%s,%s,%s)''',
        [name,sellerID,category,free,status,condition,description,price])
    conn.commit()
    itemID = getLastInsertID(conn)
    return itemID
   
   
#Retreives the id of the last inserted item.
def getLastInsertID(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select last_insert_id()''')
    itemID = curs.fetchone()
    return itemID['last_insert_id()']
     
#Update listing.

#Delete listing.


#Retrieve all listings.
def getListings(conn): 
    curs = dbi.dict_cursor(conn)
    sql  = '''select  * from item where status <> 'Sold' '''
    curs.execute(sql)
    results = curs.fetchall()
    return results



#Retrieve one listing given item id.
def getListing(conn, item_identifier): 
    curs = dbi.dict_cursor(conn)
    sql  = '''select  * from item where item_id = %s '''
    val = [item_identifier]
    curs.execute(sql, val)
    results = curs.fetchall()
    return results







#Testing.
if __name__ == '__main__':
    dbi.cache_cnf()  
    dbi.use('gem_db')
    conn = dbi.connect()
    #result = getListing(conn,5)
    #result = getListings(conn)
    #print(len(result))
    #result = insertItem(conn,"shirt","Clothing",False,"red","Brand New","10.50")
    #print(result.f)
    #result = insertListing(conn,"shirt","red")

    insertListing(conn, "my sanity", "last hairs of insanity")
    insertListing(conn, "iphone 6 phone case", "really well  loved, but protects your phone very well")
    insertListing(conn, "clairo concert tickets", "tickets from a past concert that are so beautiful, they are frameable.")
    insertListing(conn, "refrigerator", "perfect for your room!")
    insertListing(conn, "saxophone", "in good condition, barely used! just has a few dents")
    insertListing(conn, "desk lamp", "needs a new lightbulb but besides that in perfect condition")


    insertListing(conn, "birkenstocks", "black; size 7")
    insertListing(conn, "mug", "hand made, really beautiful colors")
    insertListing(conn, "mirror", "small, really cute, great magnifying mirror")
    insertListing(conn, "winter coat", "perfect for wellesley winters. fits a bit small")
    insertListing(conn, "laundry detegent", "hypo-allergenic, brand new never used")
    insertListing(conn, "beanie", "size small, North face, fits really snug")


    result = getListings(conn)
    print(result)
    print(len(result))
    #print(result) 




    