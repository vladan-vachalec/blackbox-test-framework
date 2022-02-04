import logging

import yaml

from definitions import CONFIG_PATH
from utils.splunk.splunk_client import SplunkSearch

config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)['splunk']


class SplunkFetch:
    """ SecurityEventManager provides implementations to fetch, process events from Splunk."""
    splunk_events = []
    logger = logging.getLogger('event_processing')

    def fetch_from_splunk(self, search_query, rule_type):
        """ Responsible to Execute search and fetch security events from Splunk  using search query and index time."""
        # Init Splunk search
        splunk_events = []
        logger = logging.getLogger('event_processing')
        splunk_search = SplunkSearch(rule_type)
        offset = 0
        # Execute search and fetch events
        splunk_search.execute_search(search_query)
        while True:
            new_splunk_events = splunk_search.get_events(offset)

            self.logger.info("Found {} events".format(len(new_splunk_events)))
            self.splunk_events += new_splunk_events

            # search again if max (50000) is reached
            if len(new_splunk_events) == 50000:
                offset += 50000
            else:
                break
