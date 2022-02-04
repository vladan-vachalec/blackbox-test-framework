import requests
import yaml

from definitions import CONFIG_PATH
from utils.email import SMTPEmail

user_mailbox = '/mailbox/mymailbox'
delete_email_url = '/mailbox/mymailbox/{}'


def send_email(subject, message):
    SMTPEmail.send_email(subject, message)


def send_email_from_file(subject, input_file):
    SMTPEmail.send_email_from_file(subject, input_file)


def get_emails():
    config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)
    return requests.get(config['inbucket']['api_url'] + user_mailbox)


def delete_email(email_id):
    config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)
    return requests.delete(config['inbucket']['api_url'] + delete_email_url.format(email_id))
