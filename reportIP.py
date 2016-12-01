import calendar
import sqlite3
import requests
import time
import configparser

# Read in the config file
confPath = 'config.ini'
config = configparser.ConfigParser()
config.read(confPath)


def cget(section, name):
    """Returns a value with a given name from the configuration file."""
    return config[section][name]


# Connect to the SynoAutoBlock.db Database and retrieve all IPs reported since the last check
conn = sqlite3.connect(cget('ReportIP', 'AutoBlockDBPath'))
c = conn.cursor()
c.execute('SELECT IP FROM AutoBlockIP WHERE Deny = 1 AND RecordTime > ?', [cget('ReportIP', 'LastCheck')])
result = c.fetchall()
conn.close()

# Iterate over all IPs and report them to abuseipdb.org
httpResponse = []
for ip in result:
    param = {'key': cget('AbuseIPDB', 'apiKey'), 'category': cget('AbuseIPDB', 'categories'), 'comment': cget('AbuseIPDB', 'comment'), 'ip': ip}
    r = requests.post(cget('AbuseIPDB', 'apiURL'), data=param)
    httpResponse.append(r.status_code)

# Check whether all IPs were reported successfully
success = True
for code in httpResponse:
    if code != 200:
        success = False

# Create message for the notification
if success:
    pushoverApiMessage = 'AutoBlock: ' + str(result.__len__()) + ' IPs were blocked.'
else:
    pushoverApiMessage = 'AutoBlock: Reporting IPs failed.'

# Send a notification to the User via Pushover
param = {'token': cget('Pushover', 'apiToken'), 'user': cget('Pushover', 'apiUser'), 'message': pushoverApiMessage}
requests.post(cget('Pushover', 'apiURL'), data=param)

# Save the time of this check in UTC epoch time (seconds since 01.01.1970)
config['ReportIP']['LastCheck'] = str(calendar.timegm(time.gmtime()))
with open(confPath, 'w') as configfile:
    config.write(configfile)
    configfile.close()
