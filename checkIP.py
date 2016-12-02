import requests
import configparser

# Read in the config file
confPath = '.ignore/config.ini'
config = configparser.ConfigParser()
config.read(confPath)


def cget(section, name):
    """Returns a value with a given name from the configuration file."""
    return config[section][name]

ip = requests.get('https://api.ipify.org').text
url = cget('AbuseIPDB', 'checkURL') + ip + '/json'
param = {'key': cget('AbuseIPDB', 'apiKey'), 'days': '2'}
r = requests.get(url, data=param)

if r.text == '[]':
    message = 'Auto Check: No Abuse reported.'
else:
    message = 'Auto Check: ' + r.text

# Send a notification to the User via Pushover
param = {'token': cget('Pushover', 'apiToken'), 'user': cget('Pushover', 'apiUser'), 'message': message}
requests.post(cget('Pushover', 'apiURL'), data=param)
