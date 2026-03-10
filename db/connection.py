"""Pool de conexões PostgreSQL."""
import psycopg2
from psycopg2 import pool
from config.settings import DATABASE_URL

_pool = None


def get_pool():
    """Retorna o pool de conexões (cria se não existir)."""
    global _pool
    if _pool is None:
        _pool = pool.ThreadedConnectionPool(1, 10, DATABASE_URL)
    return _pool


def get_connection():
    """Pega uma conexão do pool."""
    return get_pool().getconn()


def release_connection(conn):
    """Devolve uma conexão ao pool."""
    get_pool().putconn(conn)


def execute_query(query, params=None, fetch=True):
    """Executa query e retorna resultados."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)


def execute_many(query, params_list):
    """Executa query para múltiplos registros."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.executemany(query, params_list)
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)
