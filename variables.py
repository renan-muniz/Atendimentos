import psycopg2

conexion = psycopg2.connect(
    host = "localhost",
    database = "controle_atendimentos",
    user = "postgres",
    password = "Renan1013",
    port = 5432
)



