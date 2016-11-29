import sqlite3
import requests

confPath = 'conf.txt'
dbPath = '/etc/synoautoblock.db'
apiURL = 'https://www.abuseipdb.com/report/json'
apiKey = 'YOUR API KEY HERE'
apiCategories = '18,20'
apiComment = 'Tried to login into MailServer without Permission. Got blocked after 3 tries.'

with open(confPath) as f:
    lastIP = f.readline()

conn = sqlite3.connect(dbPath)
c = conn.cursor()

c.execute('SELECT IP FROM AutoBlockIP WHERE Deny=1')

result = c.fetchall()

textFile = open("output.txt", "w")

for item in result:
    textFile.write("%s\n" % item)

textFile.close()

conn.close()
