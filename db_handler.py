import sqlalchemy
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable


class PostgresDBHandler(object):
    """Configuration for Postgres database connections using sqlalchemy."""
    HOST = 'host'
    USER = 'user'
    PASSWORD = 'password'
    DATABASE = 'database'
    POOL_SIZE = 'pool_size'
    PORT = 'port'
    INIT_OPTS = 'init_opts'

    def __init__(self, config):
        """Create a PostgresDB handler object. It can take ConfigObj or dictionary as
        constructor parameter.
        :param {} config: Settings for connecting to the database.
        :rtype: PostgresDBHandler
        """
        self.metadata = sqlalchemy.schema.MetaData()
        self.pool_size = 5
        if config.has_key(PostgresDBHandler.POOL_SIZE):
            self.pool_size = int(config[PostgresDBHandler.POOL_SIZE])

        connect_timeout = 10 # seconds
        port = '5432'
        if PostgresDBHandler.PORT in config:
            port = config[PostgresDBHandler.PORT]

        self.db_url = sqlalchemy.engine.url.URL(
            "postgresql",
            username=config[PostgresDBHandler.USER],
            host=config[PostgresDBHandler.HOST],
            port=port,
            database=config[PostgresDBHandler.DATABASE])
        self.engine = engine = sqlalchemy.create_engine(
            self.db_url, pool_size=self.pool_size,
            connect_args={'connect_timeout': connect_timeout})
        if PostgresDBHandler.INIT_OPTS in config and \
                        'reflect_metadata' in config[PostgresDBHandler.INIT_OPTS]:
            self.metadata.reflect(bind=engine, views=True)
            self.metadata_reflected = True
        else:
            self.metadata_reflected = False

    def getEngine(self, echo=False):
        """Get database engine.
        :rtype: sqlalchemy.engine.Engine
        """
        return self.engine

    def getSession(self, expire_on_commit=True, auto_flush=True):
        """Starts a new session with the current engine and returns it  to the caller.
        It is responsibility of the callee to appropriately close the session.
        :param boolean expire_on_commit:
        :param boolean auto_flush:
        :rtype: sqlalchemy.orm.session.Session
        """
        session = sessionmaker(bind=self.getEngine(), autoflush=auto_flush,
                               expire_on_commit=expire_on_commit)
        return session()
