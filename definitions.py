import os

# https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.yml')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
FEATURES_DIR = os.path.join(ROOT_DIR, 'features')
SELENIUM_BIN = os.path.join(ROOT_DIR, 'binaries', 'selenium')
