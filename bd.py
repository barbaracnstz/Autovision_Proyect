import psycopg2

# Función para conectar a la base de datos
def conectar():
    try:
        conexion_db = psycopg2.connect(
            host="localhost",
            database="autovision",
            user="postgres",
            password="root"
        )
        return conexion_db
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def obtener_residentes():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        query = """
        SELECT r.rut_residente, r.dv_residente, r.nombre_residente, r.apellido_residente, r.telefono_residente, r.no_depto_residente, v.patente_vehiculo 
        FROM residente r
        LEFT JOIN vehiculo v ON r.rut_residente = v.residente_rut_residente;
        """
        cursor.execute(query)
        residentes = cursor.fetchall()
        conexion.close()

        lista_residentes = []
        for residente in residentes:
            lista_residentes.append({
                'rut_residente': residente[0],
                'dv_residente': residente[1],
                'nombre_residente': residente[2],
                'apellido_residente': residente[3],
                'telefono_residente': residente[4],
                'no_depto_residente': residente[5],
                'patente_vehiculo': residente[6]
            })
        return lista_residentes
    return []


# Editar la información de un residente
def editar_residente(rut_residente, nuevo_telefono, nuevo_nro_depto, nueva_patente):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()

        # Actualizar datos en la tabla residente
        query_residente = """
        UPDATE residente 
        SET telefono_residente = %s, no_depto_residente = %s 
        WHERE rut_residente = %s;
        """
        cursor.execute(query_residente, (nuevo_telefono, nuevo_nro_depto, rut_residente))

        # Actualizar patente en la tabla vehiculo
        query_vehiculo = """
        UPDATE vehiculo 
        SET patente_vehiculo = %s 
        WHERE residente_rut_residente = %s;
        """
        cursor.execute(query_vehiculo, (nueva_patente, rut_residente))

        # Guardar cambios y cerrar conexión
        conexion.commit()
        conexion.close()


# Eliminar un residente
def eliminar_residente(rut_residente):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        query_vehiculo = "DELETE FROM vehiculo WHERE rut_residente = %s;"
        cursor.execute(query_vehiculo, (rut_residente,))
        
        query_residente = "DELETE FROM residente WHERE rut_residente = %s;"
        cursor.execute(query_residente, (rut_residente,))
        
        conexion.commit()
        conexion.close()

# Agregar un nuevo residente y su vehículo
def agregar_residente(rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente, patente_vehiculo):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()

        # Consulta para insertar en la tabla residente
        query_residente = """
        INSERT INTO residente (rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_residente, (rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente))

        # Consulta para insertar en la tabla vehiculo
        query_vehiculo = """
        INSERT INTO vehiculo (patente_vehiculo, residente_rut_residente) 
        VALUES (%s, %s)
        """
        cursor.execute(query_vehiculo, (patente_vehiculo, rut_residente))

        # Confirmar cambios en la base de datos
        conexion.commit()
        conexion.close()

