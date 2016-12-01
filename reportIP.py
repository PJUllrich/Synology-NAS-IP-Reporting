import calendar
import sqlite3
import requests
import time
import configparser

confPath = 'conf.ini'
config = configparser.ConfigParser()
config.read(confPath)


def cget(name):
    """Returns a value with a given name from the configuration file."""
    return config['DEFAULT'][name]


# Connect to the SynoAutoBlock.db Database and retrieve all IPs reported since the last check
conn = sqlite3.connect(cget('AutoBlockDBPath'))
c = conn.cursor()
c.execute('SELECT IP FROM AutoBlockIP WHERE Deny = 1 AND RecordTime > ?', [cget('LastCheck')])
result = c.fetchall()
conn.close()

# Iterate over all IPs and report them to abuseipdb.org
httpResponse = []
for ip in result:
    param = {'key': cget('ApiKey'), 'category': cget('ApiCategories'), 'comment': cget('ApiComment'), 'ip': ip}
    r = requests.post(cget('ApiURL'), data=param)
    httpResponse.append(r.status_code)

success = True
for code in httpResponse:
    if code != 200:
        success = False

if success:
    pushoverApiMessage = 'AutoBlock: ' + str(result.__len__()) + ' IPs were blocked.'
else:
    pushoverApiMessage = 'AutoBlock: Reporting IPs failed.'

param = {'token': cget('PushoverApiToken'), 'user': cget('PushoverApiUser'), 'message': pushoverApiMessage}
requests.post(cget('PushoverApiURL'), data=param)

# Save the time of this check in UTC epoch time (seconds since 01.01.1970)
config['DEFAULT']['LastCheck'] = str(calendar.timegm(time.gmtime()))
with open(confPath, 'w') as configfile:
    config.write(configfile)
    configfile.close()
