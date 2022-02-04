from behave import when, step

from utils.databases.mssql import MSSQLDatabaseConnector
from utils.databases.oracle import OracleDatabaseConnector


@when('a user connects to a {db_type} database with following credentials {credentials}')
def step_impl(context, db_type, credentials):
    if db_type == 'MSSQL':
        context.db = MSSQLDatabaseConnector(credentials)
    else:
        context.db = OracleDatabaseConnector(credentials)


@step('executes a {sql_query} on the {db_type} database')
def step_impl(context, sql_query, db_type):
    context.db.execute_query(sql_query)
