import sqlite3
import requests
import time

confPath = 'conf.txt'
dbPath = '/etc/synoautoblock.db'

pushoverApiURL = 'https://api.pushover.net/1/messages.json'
pushoverApiToken = 'YOUR TOKEN HERE'
pushoverApiUser = 'YOUR USER KEY HERE'


apiURL = 'https://www.abuseipdb.com/report/json'
apiKey = 'YOUR API KEY HERE'
apiCategories = '18,20'
apiComment = 'Tried to login into MailServer without Permission. Got blocked after 3 tries.'

# Read in the last ip that was reported
with open(confPath) as f:
    lastCheck = f.readline()

# If no entry for the time of the last reported check exists or can be read, a default value is used
if lastCheck == "":
    lastCheck = "0"

# Connect to the SynoAutoBlock.db Database and retrieve all reported IPs
conn = sqlite3.connect(dbPath)
c = conn.cursor()
c.execute('SELECT IP FROM AutoBlockIP WHERE Deny = 1 AND RecordTime > ?', [lastCheck])
result = c.fetchall()
conn.close()

# Iterate over all IPs and report them to abuseipdb.org
# Stop once the ip that was reported previously is reached
for ip in result:
    requests.post(apiURL, json={'key': apiKey, 'category': apiCategories, 'comment': apiComment, 'ip': ip})

pushoverApiMessage = 'At ' + time.strftime('%l:%M%p on %b %d, %Y') + ' ' + result.__len__() + ' IPs were blocked.'
requests.post(pushoverApiURL, json={'token': pushoverApiToken, 'user': pushoverApiUser, 'message': pushoverApiMessage})

# Save the time of this check in UTC epoch time (seconds since 01.01.1970)
confFile = open(confPath, "w")
confFile.write(time.gmtime(0))
confFile.close()
