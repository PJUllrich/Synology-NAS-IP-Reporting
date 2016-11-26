import sqlite3

dbpath = '/etc/synoautoblock.db'

conn = sqlite3.connect(dbpath)
c = conn.cursor()

c.execute('SELECT {c} FROM {t} WHERE {cc}=1')\
    .__format__(c='IP', t='AutoBlockIP', cc='Deny')

result = c.fetchall()

textFile = open("output.txt", "w")
textFile.write(result)
textFile.close()

conn.close()
