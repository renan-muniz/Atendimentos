import psycopg2
from urllib.parse import urlparse
import os
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    conexion = psycopg2.connect(DATABASE_URL)

else:
    conexion = psycopg2.connect(
        host = "localhost",
        database = "controle_atendimentos",
        user = "postgres",
        password = "Renan1013",
        port = 5432,
    )



