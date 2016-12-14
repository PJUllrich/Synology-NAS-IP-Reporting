import requests
import configparser
import os
import logging

# Read in the config file
confPath = os.path.dirname(os.path.realpath(__file__)) + '/config/config.ini'
config = configparser.ConfigParser()
config.read(confPath)

# Get new Logger
logger = logging.getLogger('checkIPLogger')
logger.setLevel(logging.INFO)

# Create a Filehandler for the logger
if not os.path.exists('logs'):
    os.makedirs('logs')
fh = logging.FileHandler('logs/checkIP.log')
fh.setLevel(logging.INFO)

# Set the format of the logging output
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


# Get the external IP of the NAS
ip = requests.get('https://api.ipify.org').text

# Get the reports for the last 2 days for the external IP of the NAS
url = config['AbuseIPDB']['checkURL'] + ip + '/json'
param = {'key': config['AbuseIPDB']['apiKey'], 'days': '2'}
r = requests.get(url, data=param)

# If no report was made, simply log to the log file
# Otherwise we send a push notification via PushOver to the Admin
if r.text == '[]':
    logger.info('No abuse reported.')
else:
    message = 'AutoCheck: ' + r.text
    # Send a notification to the User via Pushover
    param = {'token': config['Pushover']['apiToken'], 'user': config['Pushover']['apiUser'], 'message': message}
    requests.post(config['Pushover']['apiURL'], data=param)
