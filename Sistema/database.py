import logging
import time
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool

from config import config

logger = logging.getLogger(__name__)


class Database:
    _connection_pool = None

    @classmethod
    def initialize(cls, intentos: int = 30, espera: float = 2.0):
        """Crea el pool de conexiones, reintentando mientras la base de datos arranca."""
        ultimo_error = None
        for intento in range(1, intentos + 1):
            try:
                cls._connection_pool = pool.ThreadedConnectionPool(
                    1, 20,
                    host=config.DB_HOST,
                    port=config.DB_PORT,
                    database=config.DB_NAME,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    connect_timeout=5,
                )
                logger.info('Pool de conexiones inicializado')
                return
            except psycopg2.OperationalError as e:
                ultimo_error = e
                logger.warning('Base de datos no disponible (intento %s/%s): %s', intento, intentos, e)
                time.sleep(espera)
        raise ultimo_error

    @classmethod
    @contextmanager
    def get_connection(cls):
        if cls._connection_pool is None:
            cls.initialize()

        connection = cls._connection_pool.getconn()
        if connection.closed:
            # Conexión rota (p. ej. la BD se reinició): se descarta y se pide otra
            cls._connection_pool.putconn(connection, close=True)
            connection = cls._connection_pool.getconn()

        descartar = False
        try:
            yield connection
            connection.commit()
        except Exception as e:
            descartar = isinstance(e, (psycopg2.OperationalError, psycopg2.InterfaceError)) or bool(connection.closed)
            try:
                connection.rollback()
            except psycopg2.Error:
                descartar = True
            logger.error(f'Error en transacción: {e}')
            raise
        finally:
            cls._connection_pool.putconn(connection, close=descartar)

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
            logger.info('Pool de conexiones cerrado')


@contextmanager
def transaction():
    """Cursor dentro de una sola transacción (commit al salir, rollback si hay error)."""
    with Database.get_connection() as connection:
        with Database.get_cursor(connection) as cursor:
            yield cursor


def execute_query(query, params=None):
    """Ejecuta una sentencia y devuelve el número de filas afectadas."""
    with transaction() as cursor:
        cursor.execute(query, params or ())
        return cursor.rowcount


def fetch_all(query, params=None):
    with transaction() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchall()


def fetch_one(query, params=None):
    with transaction() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchone()
