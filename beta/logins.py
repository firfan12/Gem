#Gem project.
#March 2021
#Rebecca, Christine, Natalie, Fatima

import cs304dbi as dbi

def get_user(conn,username):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT user,hashed
                      FROM userpass
                      WHERE user = %s''',
                     [username])
    curs.fetchall()