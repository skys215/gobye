import mysqldb
conn  = mysqldb.connect(
        db = 'gobye',
        user = 'root',
        charset='utf8'
    )
cursor = conn.cursor()
id = 
sql = 'select profess_id from plan where id ='+str(id)
cursor.execute(sql)
a = cursor.fetchone()
cursor.close()
conn.close()