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

#Testing.
if __name__ == '__main__':
    dbi.cache_cnf()  
    dbi.use('gem_db')
    conn = dbi.connect()
    result = insertListing(conn,"shirt","red")
    print(result) 