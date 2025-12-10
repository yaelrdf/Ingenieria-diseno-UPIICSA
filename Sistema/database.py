import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import logging
from config import config

logger = logging.getLogger(__name__)

class Database:
    _connection_pool = None
    
    @classmethod
    def initialize(cls):
        try:
            cls._connection_pool = pool.SimpleConnectionPool(
                1, 20,
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            logger.info("Pool de conexiones inicializado")
        except Exception as e:
            logger.error(f"Error al inicializar el pool: {e}")
            raise
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        if cls._connection_pool is None:
            cls.initialize()
        
        connection = cls._connection_pool.getconn()
        try:
            yield connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error(f"Error en transacción: {e}")
            raise
        finally:
            cls._connection_pool.putconn(connection)
    
    @classmethod
    @contextmanager
    def get_cursor(cls, connection):
        cursor = connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    @classmethod
    def close_all(cls):
        if cls._connection_pool:
            cls._connection_pool.closeall()
            logger.info("Pool de conexiones cerrado")

# Funciones de utilidad para la base de datos
def execute_query(query, params=None):
    with Database.get_connection() as connection:
        with Database.get_cursor(connection) as cursor:
            cursor.execute(query, params or ())
            return cursor

def fetch_all(query, params=None):
    with Database.get_connection() as connection:
        with Database.get_cursor(connection) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

def fetch_one(query, params=None):
    with Database.get_connection() as connection:
        with Database.get_cursor(connection) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()