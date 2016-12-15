import calendar
import sqlite3

import logging
import requests
import time
import configparser
import os

# Read in the config file
confPath = os.path.dirname(os.path.realpath(__file__)) + '/config/config.ini'
config = configparser.ConfigParser()
config.read(confPath)

# Get new Logger
logger = logging.getLogger('reportIPLogger')
logger.setLevel(logging.INFO)

# Create a Filehandler for the logger
logPath = os.path.dirname(os.path.realpath(__file__)) + '/logs'
if not os.path.exists(logPath):
    os.makedirs(logPath)
fh = logging.FileHandler(logPath + '/reportIP.log')
fh.setLevel(logging.INFO)

# Set the format of the logging output
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


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
    r = requests.post(cget('AbuseIPDB', 'reportURL'), data=param)
    httpResponse.append(r.status_code)

# Check whether all IPs were reported successfully
success = True
for code in httpResponse:
    if code != 200:
        success = False

# Create message for the notification
if success:
    message = 'AutoBlock: ' + str(result.__len__()) + ' IPs were blocked.'
else:
    message = 'AutoBlock: Reporting IPs failed.'

# Log this event to the log file
logger.info(message)

# Send a notification to the User via Pushover
param = {'token': cget('Pushover', 'apiToken'), 'user': cget('Pushover', 'apiUser'), 'message': message}
requests.post(cget('Pushover', 'apiURL'), data=param)

# Save the time of this check in UTC epoch time (seconds since 01.01.1970)
config['ReportIP']['LastCheck'] = str(calendar.timegm(time.gmtime()))
with open(confPath, 'w') as configfile:
    config.write(configfile)
    configfile.close()
