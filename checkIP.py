import requests
import configparser
import os
import logging

# Read in the config file
confPath = os.path.dirname(os.path.realpath(__file__)) + '/config.ini'
config = configparser.ConfigParser()
config.read(confPath)

logging.config.dictConfig()
logger = logging.getLogger(__name__)

def cget(section, name):
    """Returns a value with a given name from the configuration file."""
    return config[section][name]

ip = requests.get('https://api.ipify.org').text
url = cget('AbuseIPDB', 'checkURL') + ip + '/json'
param = {'key': cget('AbuseIPDB', 'apiKey'), 'days': '2'}
r = requests.get(url, data=param)

if r.text != '[]':
    message = 'AutoCheck: ' + r.text
    # Send a notification to the User via Pushover
    param = {'token': cget('Pushover', 'apiToken'), 'user': cget('Pushover', 'apiUser'), 'message': message}
    requests.post(cget('Pushover', 'apiURL'), data=param)
