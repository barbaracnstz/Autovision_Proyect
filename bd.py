import psycopg2

def conectar():
    try:
        # Crear la conexión a la base de datos PostgreSQL
        conexion_db = psycopg2.connect(
            host="localhost",
            database="autovision",
            user="postgres",
            password="1234"
        )
        return conexion_db
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None
