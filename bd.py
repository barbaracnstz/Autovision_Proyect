import psycopg2

# Función para conectar a la base de datos
def conectar():
    try:
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

def obtener_datos_residentes(self):
        conexion = conectar()
        if not conexion:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return []

        cursor = conexion.cursor()
        query = """SELECT rut_residente, nombre_residente, telefono_residente, no_depto_residente, patente_vehiculo 
                   FROM residente LEFT JOIN vehiculo ON residente.rut_residente = vehiculo.residente_rut_residente"""
        cursor.execute(query)
        datos = cursor.fetchall()
        conexion.close()
        return datos

# Editar la información de un residente
def editar_residente(rut, nuevo_nombre, nuevo_telefono, nuevo_nro_depto, nueva_patente):
    conexion = conectar()  # Conexión a la base de datos
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            UPDATE residente SET 
                nombre_residente = %s,
                telefono_residente = %s,
                no_depto_residente = %s
            WHERE rut_residente = %s
        """, (nuevo_nombre, nuevo_telefono, nuevo_nro_depto, rut))
        
        # Actualizar la patente en la tabla de vehículos
        if nueva_patente:  # Solo actualizamos si se proporciona una nueva patente
            cursor.execute("""
                UPDATE vehiculo SET 
                    patente_vehiculo = %s
                WHERE residente_rut_residente = %s
            """, (nueva_patente, rut))
        
        conexion.commit()  # Confirmar los cambios
    except Exception as e:
        print(f"Error al editar residente: {e}")
    finally:
        cursor.close()
        conexion.close()

# Eliminar un residente
def eliminar_residente(rut_residente):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            # Eliminar primero el vehículo asociado al residente
            query_vehiculo = "DELETE FROM vehiculo WHERE residente_rut_residente = %s;"  # Asegúrate de usar el nombre correcto
            cursor.execute(query_vehiculo, (rut_residente,))
            
            # Luego eliminar el residente
            query_residente = "DELETE FROM residente WHERE rut_residente = %s;"
            cursor.execute(query_residente, (rut_residente,))
            
            conexion.commit()
        except Exception as e:
            print(f"Error al eliminar residente: {e}")  # Puedes ajustar esto a un log o mensaje
        finally:
            conexion.close()
    else:
        print("Error: No se pudo conectar a la base de datos.")



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
        
def cargar_datos():
    conexion = conectar()  # Conexión a la base de datos
    cursor = conexion.cursor()
    try:
        query = """SELECT rut_residente, nombre_residente, telefono_residente, no_depto_residente, patente_vehiculo 
                   FROM residente LEFT JOIN vehiculo ON residente.rut_residente = vehiculo.residente_rut_residente"""
        cursor.execute(query)
        registros = cursor.fetchall()
        return registros
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


