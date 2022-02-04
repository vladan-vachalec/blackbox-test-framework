import json
import os
import smtplib
from pathlib import Path

import yaml

from definitions import CONFIG_PATH
from definitions import DATA_DIR
from definitions import ROOT_DIR


def send_email(timestamp, message):
    email_json = os.path.join(ROOT_DIR, 'data', 'email', 'test_email.json')
    with open(email_json) as f:
        email_data = json.load(f)

    subject = email_data['subject'].format(timestamp)
    message = "From: {}\r\nTo: {}\r\nSubject: {}\r\n\r\n{}" \
        .format(email_data['from'], ", ".join(email_data['to']), subject, message)

    config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)

    try:
        server = smtplib.SMTP(config['inbucket']['hostname'], 25)
        server.sendmail(email_data['from'], email_data['to'], message)
        print(message)
    except smtplib.SMTPDataError as inst:
        print('Email has been blocked: {}'.format(inst))


def send_email_from_file(subject, input_file_name):
    # searches recursively in DATA_DIR for input_file_name
    for path in Path(DATA_DIR).rglob(input_file_name):
        with open(path) as input_file:
            message = input_file.read()
    try:
        send_email(subject, message)
    except UnboundLocalError as e:
        e_message = "Test skipped. Cannot find file: '{}' anywhere in '{}' directory".format(input_file_name, DATA_DIR)
        raise FileNotFoundError(e_message)
