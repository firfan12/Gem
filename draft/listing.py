#Gem project.
#March 2021
#Rebecca, Christine, Natalie, Fatima

import cs304dbi as dbi

#For the time being, there is one seller and her ID is:
sellerID = "rarango@wellesley.edu"


#Retreives the id of the last inserted item.
def getLastInsertID(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select last_insert_id()''')
    itemID = curs.fetchone()
    return itemID['last_insert_id()']



#Update listing.
    #Will implement later. 


#Delete listing.
    #Will implement later. 


#Retrieve all listings that are not marked as Sold.
def getListings(conn): 
    curs = dbi.dict_cursor(conn)
    sql  = '''select  * from item where status <> 'Sold' '''
    curs.execute(sql)
    results = curs.fetchall()
    return results


#Retrieve the listing corresponding to a given item id.
def getListing(conn, item_identifier): 
    curs = dbi.dict_cursor(conn)
    sql  = '''select  * from item where item_id = %s '''
    val = [item_identifier]
    curs.execute(sql, val)
    results = curs.fetchall()
    return results


#Insert new listing; returns the auto-incremented ID of that listing.
#Draft:
def insertListing(conn,name,category,free,description,condition,price):
    status = 'Still Available'
    curs = dbi.dict_cursor(conn)
    #For now, image not implemented. Using hardcoded image for the draft.
    curs.execute('''
        insert into item(item_name,seller_id,category,free,status,item_condition,
                        item_description,price)
        values (%s,%s,%s,%s,%s,%s,%s, %s)''',
        [name,sellerID,category,free,status,condition,description,price]) 
    conn.commit()
    itemID = getLastInsertID(conn)
    return itemID

   


#Testing.
if __name__ == '__main__':
    dbi.cache_cnf()  
    dbi.use('gem_db')
    conn = dbi.connect()
    #result = getListing(conn,5)
    #result = getListings(conn)
    #print(len(result))
    #result = insertListing(conn,"shirt","Clothing",False,"red","Brand New","10.50")
    #print(result.f)
    #result = insertListing(conn,"shirt","red")

    result = getListings(conn)
    print(result)
    print(len(result))
    #print(result) 




    