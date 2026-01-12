import os
import psycopg2

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        dbname="controle_atendimentos",
        user="postgres",
        password="Renan1013",
        host="localhost",
        port="5432"
    )


