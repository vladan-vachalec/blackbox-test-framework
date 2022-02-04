import json
import os
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
import yaml

from definitions import CONFIG_PATH

config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)['splunk']


class SplunkSearch:
    def __init__(self, rule_type):
        self.user_name = config['SPLUNK_USER_NAME']
        self.password = config['SPLUNK_PASSWORD']
        self.job_service_url = config['SPLUNK_JOB_SERVICE_URL']
        self.base_url = config['SPLUNK_BASE_URL']

        self.job_id = None
        self.session_key = None
        self.get_session_key()
        self.splunk_path = "os.path.join(SPLUNK_EVENTS_DIR, '{}.json'.format(rule_type))"

    def check_search_status(self):
        search_status_request = requests.get(f"{self.base_url}{self.job_service_url}/{self.job_id}/",
                                             params={'output_mode': 'json'},
                                             headers={'Authorization': 'Splunk %s' % self.session_key},
                                             auth=(self.user_name, self.password),
                                             verify=config['REQUESTS_VERIFY_CERTIFICATE_SPLUNK'])
        return json.loads(search_status_request.text)["entry"][0]["content"]["isDone"]

    def get_session_key(self):
        # Authenticate with server.
        # Disable SSL cert validation. Splunk certs are self-signed.
        server_content = requests.post("/".join([self.base_url.strip("/"), 'services/auth/login']),
                                       data=urlencode({'username': self.user_name, 'password': self.password}),
                                       verify=config['REQUESTS_VERIFY_CERTIFICATE_SPLUNK'],
                                       params={'output_mode': 'json'})
        self.session_key = json.loads(server_content.text)["sessionKey"]

    def execute_search(self, search_query):
        time.sleep(120)
        if not search_query.startswith("search"):
            search_query = "search " + search_query

        search_request = requests.post(
            f"{self.base_url}{self.job_service_url}",
            headers={'Authorization': 'Splunk %s' % self.session_key},
            params={'output_mode': 'json', },
            data=urlencode({'search': search_query}),
            auth=(self.user_name, self.password),
            verify=config['REQUESTS_VERIFY_CERTIFICATE_SPLUNK'])
        try:
            self.job_id = json.loads(search_request.text)["sid"]
            return True
        except KeyError as e:
            print("Executing search failed with message {}".format(e.message))
            return False

    def get_events(self, offset=0):

        while not self.check_search_status():
            time.sleep(10)

        result_request = requests.get(
            f"{self.base_url}{self.job_service_url}/{self.job_id}/results/{self.job_id}/?offset={offset}&count=50000",
            params={
                'output_mode': 'json',
            },
            auth=(self.user_name, self.password),
            verify=config['REQUESTS_VERIFY_CERTIFICATE_SPLUNK']
        )

        if os.path.isfile(self.splunk_path):
            os.remove(self.splunk_path)

        assert result_request.text is not None, "The request is empty"
        with open(self.splunk_path, 'wb') as f:
            f.write(result_request.text.encode('UTF-8'))

        results = json.loads(result_request.text)
        return results["results"]

    def check_event_time(self):
        with open(self.splunk_path) as json_file:
            json_data = json.load(json_file)['results']
            for item in json_data:
                event_time = int(item['_indextime'])
                event_time = datetime.fromtimestamp(event_time)
                current_time = datetime.now()
                diff = current_time - event_time
                assert diff < timedelta(minutes=5), "The event is not current."
