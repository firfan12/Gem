import cs304dbi as dbi

#For the time being, there is one seller and her ID is:
sellerID = "rarango@wellesley.edu"

#Insert new listing; returns the auto-incremented ID of that listing.
#Draft:
def insertItem(conn,name,category,description,condition,price):
    status = 'Still Available'
    curs = dbi.dict_cursor(conn)
    #For now, no image.
    curs.execute('''
        insert into item(item_name,seller_id,category,status,item_condition,item_description,price)
        values (%s,%s,%s,%s,%s,%s,%s)''',
        [name,sellerID,category,status,condition,description,price]) 
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
def getListing(conn, itemID): 
    curs = dbi.dict_cursor(conn)
    sql  = '''select  * from item where item_id = %s '''
    val = [itemID]
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
    #print(len(result))
    #result = insertItem(conn,"shirt","Clothing",False,"red","Brand New","10.50")
    #print(result.f)
    print(result) 

