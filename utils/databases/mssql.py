import pyodbc
import yaml

from definitions import CONFIG_PATH


class MSSQLDatabaseConnector:

    def __init__(self, credentials):
        mssql_config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)['databases']['mssql']
        self.connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + mssql_config['server'] + ';DATABASE=' + mssql_config[
                'database'] + ';UID=' + credentials['username'] + ';PWD=' + credentials['password'])
        self.cursor = self.connection.cursor()

    def execute_query(self, query):
        try:
            return self.cursor.execute(query)
        except pyodbc.Error as ex:
            print(ex.args[1])
