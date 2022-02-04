import cx_Oracle
import yaml

from definitions import CONFIG_PATH


class OracleDatabaseConnector:

    def __init__(self, credentials):
        oracle_config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)['database']['oracle']
        self.connection = cx_Oracle.connect(user=credentials['username'], password=credentials['password'],
                                            dsn=oracle_config['dsn'])
        self.cursor = self.connection.cursor()

    def execute_query(self, query):
        return self.cursor.execute(query)
