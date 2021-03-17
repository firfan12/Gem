import cs304dbi as dbi

#Insert new listing.
def insertListing(conn, description):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        insert into 
    ''')
    
#Update listing.

#Delete listing.

#Testing.
if __name__ == '__main__':
    dbi.cache_cnf()  
    dbi.use('rarango_db')
    conn = dbi.connect()