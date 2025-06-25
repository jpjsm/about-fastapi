from os import getenv

from dbaccess import DB_Access

ICECREAM_DB_HOST = getenv('ICECREAM_DB_HOST', '192.168.1.95')
ICECREAM_DB_PORT = getenv('ICECREAM_DB_PORT', '5432')
ICECREAM_DB_NAME = getenv('ICECREAM_DB_NAME', 'icecream')
ICECREAM_DB_USER = getenv('ICECREAM_DB_USER', 'icecream')
ICECREAM_DB_PWD = getenv('ICECREAM_DB_PWD', 'ABCdef123!')

# default port is 10301 if APP_PORT is not defined
APP_PORT = getenv('APP_PORT', 10301)

# Validate DB info
icecream_vars = [ICECREAM_DB_HOST, ICECREAM_DB_PORT, ICECREAM_DB_NAME, ICECREAM_DB_USER, ICECREAM_DB_PWD]
if not all(icecream_vars):
    raise Exception("One or more database environment variables are missing.")

db_access = DB_Access(
    db_host=ICECREAM_DB_HOST,
    db_port=ICECREAM_DB_PORT,
    db_name=ICECREAM_DB_NAME,
    db_user=ICECREAM_DB_USER,
    db_pass=ICECREAM_DB_PWD
)
Pool = db_access.ConnectionPool