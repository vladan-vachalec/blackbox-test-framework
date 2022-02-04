from urllib.parse import urlparse

import requests.adapters
from exchangelib import DELEGATE, Account, Credentials, Configuration, Message
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter

"""
This script provides a possibility to check connection to Exchange server without a need to run the whole test suite.
It's following examples from: https://ecederstrand.github.io/exchangelib/ -> for more info, check the documentation.

How to run this script? Simply run "python exchange_connection_checker.py"

Configuration:
You need to have the following information regarding the exchange server you want to connect to:
1. server, e.g. webmail.mycompany.com
2. primary_smtp_address, e.g. user@mycompany.com
3. credentials, e.g. myuser@mycompany.com/secret_password
Optional:
4. certificate/certificates/certificate chain to validate when making a connection (follow README.md instructions,\
in order to generate a certificate properly)
5. proxy server details

HTTP_ADAPTERS
First line in the "main" method of this script enables HTTP adapters, you can use only one of them.\
Always uncomment only one at a time.

    BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter
    - exchangelib provides a sample adapter which ignores TLS validation errors. Use at own risk.
    
    BaseProtocol.HTTP_ADAPTER_CLS = ProxyAdapter
    - custom root certificates depending on the server to connect to
    
    BaseProtocol.HTTP_ADAPTER_CLS = RootCAAdapter
    - proxy support
"""


class RootCAAdapter(requests.adapters.HTTPAdapter):
    """An HTTP adapter that uses a custom root CA certificate at a hard coded location"""

    def cert_verify(self, conn, url, verify, cert):
        # print(ssl.get_default_verify_paths())
        cert_file = {
            '{server domain (e.g. webmail.mycompany.com}': '{path to the certificate you want to verify}'
        }[urlparse(url).hostname]
        try:
            super().cert_verify(conn=conn, url=url, verify=cert_file, cert=cert)
        except OSError:
            print('Could not find a suitable TLS CA certificate bundle, invalid path: {}'.format(cert_file))


class ProxyAdapter(requests.adapters.HTTPAdapter):
    def send(self, *args, **kwargs):
        kwargs['proxies'] = {
            'http': 'http://10.0.0.1:1243',
            'https': 'http://10.0.0.1:4321',
        }
        return super().send(*args, **kwargs)


if __name__ == "__main__":
    BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter
    # BaseProtocol.HTTP_ADAPTER_CLS = ProxyAdapter
    # BaseProtocol.HTTP_ADAPTER_CLS = RootCAAdapter

    ##### FOR LOGGING #####
    import logging
    from exchangelib.util import PrettyXmlHandler

    logging.basicConfig(level=logging.DEBUG, handlers=[PrettyXmlHandler()])

    credentials = Credentials(username="{username}", password="{password}")
    config = Configuration(server='{server}', credentials=credentials)
    account = Account(primary_smtp_address="{primary_smtp_address}", config=config,
                      autodiscover=False, access_type=DELEGATE)
    m = Message(
        account=account,
        subject='subject',
        body='bodytext',
        to_recipients='non@existing.email'
    )
    # m.send()
