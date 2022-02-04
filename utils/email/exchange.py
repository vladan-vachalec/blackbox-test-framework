import os
import time
from pathlib import Path
from urllib.parse import urlparse

import requests.adapters
import yaml
from exchangelib import Credentials, Account, Configuration, Mailbox, Message, DELEGATE, FileAttachment
from exchangelib.protocol import BaseProtocol

from definitions import CONFIG_PATH, DATA_DIR


def get_cert_path(path_to_check):
    from definitions import DATA_DIR
    certificate = path_to_check if os.path.isfile(path_to_check) else os.path.join(DATA_DIR, 'certificates',
                                                                                   'my_certificate.crt')
    return certificate


class RootCAAdapter(requests.adapters.HTTPAdapter):
    """An HTTP adapter that uses a custom root CA certificate at a hard coded location"""

    def cert_verify(self, conn, url, verify, cert):
        exchange_config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)['exchange']
        certification_path = get_cert_path(exchange_config['certificate_path'])
        cert_file = {
            exchange_config['server']: certification_path
        }[urlparse(url).hostname]
        try:
            super().cert_verify(conn=conn, url=url, verify=cert_file, cert=cert)
        except OSError:
            print('Could not find a suitable TLS CA certificate bundle, invalid path: {}'.format(cert_file))


class ExchangeConnector:
    try:
        exchange_config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)['exchange']
    except (FileNotFoundError, KeyError):
        exchange_config = False
        pass
    if exchange_config and os.path.isfile(get_cert_path(exchange_config['certificate_path'])):
        # Tell exchangelib to use this adapter class instead of the default

        BaseProtocol.HTTP_ADAPTER_CLS = RootCAAdapter

        credentials = Credentials(exchange_config['credentials']['username'],
                                  exchange_config['credentials']['password'])
        configuration = Configuration(server=exchange_config['server'], credentials=credentials)
        account = Account(exchange_config['primary_smtp_address'], config=configuration,
                          credentials=credentials,
                          autodiscover=exchange_config['autodiscover'],
                          access_type=DELEGATE)


def get_emails(email_count):
    return ExchangeConnector.account.inbox.all().order_by('-datetime_received')[:email_count]


def send_email(subject, input_file, is_attachment):
    for path in Path(DATA_DIR).rglob(input_file):
        with open(path, 'rb') as f:
            file_content = f.read()
    try:
        body = file_content.decode("utf-8") if not is_attachment else 'Input file sent as an attachment'
        m = Message(
            account=ExchangeConnector.account,
            folder=ExchangeConnector.account.sent,
            subject=subject,
            body=body,
            to_recipients=[Mailbox(email_address=ExchangeConnector.exchange_config['destination_email'])]
        )
        if is_attachment:
            file_attachment = FileAttachment(name=input_file, content=file_content)
            m.attach(file_attachment)
        m.send_and_save()
    except UnboundLocalError as e:
        e_message = "Test skipped. Cannot find file: '{}' anywhere in '{}' directory".format(input_file, DATA_DIR)
        raise FileNotFoundError(e_message)


def find_email(subject, email_count=2):
    # loop to find the latest email and timestamp subject in it
    timeout = 10
    step_time = 2
    email_found = False
    for _ in range(1, timeout // step_time):
        if email_found:
            break
        time.sleep(step_time)
        emails = get_emails(email_count)
        for email in emails:
            if email.subject.endswith(subject):
                email_found = True
                break
    return email_found
