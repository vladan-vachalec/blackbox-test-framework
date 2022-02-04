import logging
import os

import yaml
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.exposition import basic_auth_handler

from definitions import CONFIG_PATH

config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)


def prometheus_auth_handler(url, method, timeout, headers, data):
    if config['prometheus']['username']:
        try:
            username = config['prometheus']['username']
            password = config['prometheus']['password']
            return basic_auth_handler(url, method, timeout, headers, data, username, password)
        except KeyError as e:
            logging.warning(f'{e} Key username not found')
    else:
        return basic_auth_handler(url, method, timeout, headers, data)


def push_metric(job_name, metric_name, metric_description, medium, value=None, use_proxy=False):
    url = config['prometheus']['pushgateway_url']
    if use_proxy:
        try:
            os.environ['HTTP_PROXY'] = config['prometheus']['http_proxy']
            os.environ['HTTPS_PROXY'] = config['prometheus']['https_proxy']
        except KeyError as e:
            logging.warning(f'{e} configuration property is missing in the config file')

    registry = CollectorRegistry()
    g = Gauge(metric_name, metric_description,
              registry=registry)
    if value is not None:
        g.set(value)
    else:
        g.set_to_current_time()
    grouping_keys = None
    if medium:
        grouping_keys = {
            "medium": medium
        }
    push_to_gateway(url,
                    job=job_name,
                    grouping_key=grouping_keys,
                    registry=registry,
                    handler=prometheus_auth_handler)
