import sqlite3

dbpath = '/etc/synoautoblock.db'

conn = sqlite3.connect(dbpath)
c = conn.cursor()

c.execute('SELECT IP FROM AutoBlockIP WHERE Deny=1')
result = c.fetchall()

textFile = open("output.txt", "w")
textFile.write(result)
textFile.close()

conn.close()