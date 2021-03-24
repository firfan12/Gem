#Gem project/application.
#Rebecca, Christine, Natalie, Fatima
#March 2021

import cs304dbi as dbi

#For the time being, there is one seller and her ID is:
sellerID = "rarango@wellesley.edu"

#In the beta version, the seller will be added to the person table when they create an account. 
#We have not implemented the creating of the account yet. Instead, we are inserting the account 
#associated with this seller id manually in the
#terminal for the draft version. This adds the account to the person table:
#insert into person(name, email, password) values('Rebecca', 'rarango@wellesley.edu', 'sdfd');


#Retreives the id of the last inserted item.
def getLastInsertID(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select last_insert_id()''')
    itemID = curs.fetchone()
    return itemID['last_insert_id()']

#Update listing.
    #Will implement later for alpha version. 


#Delete listing.
    #Will implement later for alpha version.  


#Retrieve all listings that are not marked as Sold.
def getListings(conn): 
    curs = dbi.dict_cursor(conn)
    sql  = '''select * from item where status <> 'Sold' '''
    curs.execute(sql)
    results = curs.fetchall()
    return results


#Retrieve the listing that corresponds to the provided item identifier.
def getListing(conn, item_identifier): 
    curs = dbi.dict_cursor(conn)
    sql  = '''select * from item where item_id = %s '''
    val = [item_identifier]
    curs.execute(sql, val)
    results = curs.fetchone()
    return results


#Insert new listing; returns the auto-incremented ID of that listing.
#Draft version, may modify for alpha version.
def insertListing(conn,name,category,free,description,condition,price, availableForMode):
    status = 'Still Available'
    curs = dbi.dict_cursor(conn)
    #For now, storing the image in the database is not implemented. 
    #Using hardcoded image for the draft.
    #For the alpha version, we will change our database, such as changing where the 
    #photo is stored, possibly, since we learned how to do File Uploads correctly today
    #in class.
    curs.execute('''insert into item(item_name,seller_id,category,free,status,item_condition,
                item_description,price, sellmode)
                values (%s,%s,%s,%s,%s,%s,%s, %s, %s)''',
                [name,sellerID,category,free,status,condition,description,price, availableForMode]) 
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




    