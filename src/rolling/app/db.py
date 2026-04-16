import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor

from rolling.app.config import dbSettings

def get_connection() -> PgConnection:
    return psycopg2.connect(host=dbSettings.db_host,
                            port=dbSettings.db_port,
                            dbname=dbSettings.db_name,
                            user=dbSettings.db_user,
                            password=dbSettings.db_pass,
                            cursor_factory=RealDictCursor
                            )