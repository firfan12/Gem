import cs304dbi as dbi

seller_id = "rarango@wellesley.edu"

#Insert new listing.
def insertListing(conn,name,description):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        insert into item(item_name,seller_id,item_description)
        values (%s,%s,%s)''',
        [name,seller_id,description])
    conn.commit()
    return "insertListing function finished"
    
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
    val = [item_id]
    curs.execute(sql, val)
    results = curs.fetchall()
    return results


#Testing.
if __name__ == '__main__':
    dbi.cache_cnf()  
    dbi.use('gem_db')
    conn = dbi.connect()
    result = getListings(conn)
    print(result)
    print(len(result))

    #result = insertListing(conn,"shirt","red")
    #print(result) 

