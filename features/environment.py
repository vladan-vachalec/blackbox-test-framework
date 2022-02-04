import logging
import os
import shutil
import sys
from urllib.error import URLError

import yaml
from behave.log_capture import capture

from definitions import CONFIG_DIR, ROOT_DIR
from monitoring.prometheus import push_metric
from utils.selenium.selenium_service import SeleniumService

tags = ['monitoring']


def before_all(context):
    context.config.setup_logging()
    config_file = context.config.userdata.get("config")
    if config_file:
        config_file_path = os.path.join(CONFIG_DIR, '{}.yml'.format(config_file))
        if not os.path.isfile(config_file_path):
            logging.error(
                'Configuration file on this path {} does not exist,provide the file as described in Readme.'.format(
                    config_file_path))
            sys.exit(1)
    else:
        config_file_path = os.path.join(CONFIG_DIR, 'config.yml')
    dest_config_path = os.path.join(ROOT_DIR, 'config.yml')
    shutil.copy(config_file_path, dest_config_path)
    try:
        set_email_client(context)
    except KeyError:
        logging.warning('Key exchange not found')


@capture
def after_scenario(context, Scenario):
    for tag in tags:
        if tag in Scenario.tags:
            job_name = Scenario.name.lower().replace(" ", "_").replace("-", "_")[16:-9]
            if not hasattr(context, 'medium'):
                context.medium = None
            if not hasattr(context, 'expected_subject'):
                context.expected_subject = ''
            file_name = context.expected_subject.lower().split('.txt', 1)[0]
            try:
                push_metrics(job_name, file_name, context.medium, Scenario.status.name)
            except URLError:
                logging.warning("Can't reach Prometheus server, retrying with proxy")
                push_metrics(job_name, file_name, context.medium, Scenario.status.name, use_proxy=True)


@capture
def after_feature(context, Feature):
    if SeleniumService.driver:
        SeleniumService.driver.close()


def push_metrics(job_name, file_name, medium, status, use_proxy=False):
    # (<Status.passed: 2>, <Status.failed: 3>, <Status.skipped: 1>) -> set this mapping in Grafana
    # Workaround to display passed tests green in grafana

    grafana_test_status = {
        "passed": 1,
        "failed": 0,
        "skipped": 0.5
    }
    push_metric(job_name=job_name + file_name, metric_name='tr_' + job_name + file_name,
                metric_description='Test result',
                medium=medium, value=grafana_test_status[status], use_proxy=use_proxy)
    push_metric(job_name='timestamp_' + job_name + file_name, metric_name='timestamp_' + job_name + file_name,
                metric_description='Test last run',
                medium=medium, use_proxy=use_proxy)


def set_email_client(context):
    """Sets context value for email client and is_attachment based on configuration file.
     Emails will be sent via Inbucket or Exchange. Test data will be sent either as email body or an attachment"""
    config_file = yaml.load(open(os.path.join(ROOT_DIR, 'config.yml'), 'r'), Loader=yaml.FullLoader)
    context.use_exchange = False if 'inbucket' in config_file else True
    context.send_attachments = config_file['exchange']['send_attachments'] if context.use_exchange else \
        config_file['inbucket']['send_attachments']
