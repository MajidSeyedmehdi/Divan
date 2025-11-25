import pyodbc
from testpro import settings


def connect_db():
    db_settings = settings.DATABASES['default']
    conn_str = (
        f"DRIVER={db_settings['OPTIONS']['driver']};"
        f"SERVER={db_settings['HOST']},{db_settings['PORT']};"
        f"DATABASE={db_settings['NAME']};"
        f"UID={db_settings['USER']};"
        f"PWD={db_settings['PASSWORD']};"
    )
    return pyodbc.connect(conn_str)