import os
import psycopg2

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada no Render (Environment).")
    return psycopg2.connect(database_url)

conexion = get_connection()
