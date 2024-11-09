import psycopg2
from tkinter import messagebox 


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
##CRUD

# Función para insertar un nuevo residente en la base de datos
# def insertar_residente(rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente, patente_vehiculo):
#     conexion = conectar()
#     if conexion:
#         try:
#             cursor = conexion.cursor()
            
#             # Insertar residente
#             query_residente = """
#             INSERT INTO residente (rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente)
#             VALUES (%s, %s, %s, %s, %s, %s, %s);
#             """
#             cursor.execute(query_residente, (rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente))
            
#             # Insertar vehículo si se proporciona patente
#             if patente_vehiculo:
#                 query_vehiculo = """
#                 INSERT INTO vehiculo (patente_vehiculo, residente_rut_residente)
#                 VALUES (%s, %s);
#                 """
#                 cursor.execute(query_vehiculo, (patente_vehiculo, rut_residente))
            
#             # Commit y cierre de conexión
#             conexion.commit()
#             cursor.close()
#         except Exception as e:
#             print(f"Error al insertar residente o vehículo: {e}")
#         finally:
#             conexion.close()
        
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

# En bd.py

import psycopg2
from tkinter import messagebox

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

# Función para editar un residente en la base de datos
def editar_residente(rut_residente, nombre_residente, telefono_residente, no_depto_residente, patente_vehiculo):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()

            # Actualizar datos del residente
            query_residente = """
            UPDATE residente
            SET nombre_residente = %s, telefono_residente = %s, no_depto_residente = %s
            WHERE rut_residente = %s;
            """
            cursor.execute(query_residente, (nombre_residente, telefono_residente, no_depto_residente, rut_residente))

            # Si hay patente, actualizar datos del vehículo
            if patente_vehiculo:
                query_vehiculo = """
                UPDATE vehiculo
                SET patente_vehiculo = %s
                WHERE residente_rut_residente = %s;
                """
                cursor.execute(query_vehiculo, (patente_vehiculo, rut_residente))

            conexion.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al editar residente: {e}")
            messagebox.showerror("Error", "Hubo un problema al actualizar los datos del residente.")
        finally:
            conexion.close()

########################################################        ADMIN
def cargar_datos_admins(texto_busqueda=""):
    """Cargar los datos de los administradores desde la base de datos."""
    conn = conectar()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
    SELECT rut_admin, nombre_admin, apellido_admin, telefono_admin, correo_admin, cargo, estado
    FROM administrador
    """
    
    # Si hay texto de búsqueda, aplicar filtro a nombre, apellido o correo
    if texto_busqueda:
        query += " WHERE nombre_admin ILIKE %s OR apellido_admin ILIKE %s OR correo_admin ILIKE %s"
        cursor.execute(query, (f"%{texto_busqueda}%", f"%{texto_busqueda}%", f"%{texto_busqueda}%"))
    else:
        cursor.execute(query)

    # Obtener los resultados y devolverlos
    registros = cursor.fetchall()
    conn.close()
    return registros

def admin(rut_admin):
    """Cargar los datos del administrador específico desde la base de datos."""
    conn = conectar()
    if conn is None:
        return None

    cursor = conn.cursor()
    query = """
    SELECT rut_admin, dv_admin, nombre_admin, apellido_admin, telefono_admin, correo_admin, cargo
    FROM administrador
    WHERE rut_admin = %s
    """
    cursor.execute(query, (rut_admin,))
    admin_data = cursor.fetchone()
    conn.close()
    return admin_data


###RESIDENTEEEEEEEEEEE
# Función para ejecutar consultas SQL (con manejo de errores)
def ejecutar_consulta(query, params=()):
    try:
        conn = conectar()  # Asegúrate de que conectar() esté configurada correctamente
        cursor = conn.cursor()
        cursor.execute(query, params)
        resultado = cursor.fetchall()  # Usar fetchall() para obtener los resultados
        conn.commit()
        cursor.close()
        conn.close()
        return resultado
    except Exception as e:
        print(f"Error al ejecutar consulta: {e}")
        return None



# def insertar_residente(conn, rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente, patente_vehiculo):
#     # Primero, verificamos si ya existe un residente con ese rut
#     consulta_existente_residente = """
#     SELECT COUNT(*) FROM residente WHERE rut_residente = %s
#     """
#     resultado_residente = ejecutar_consulta(consulta_existente_residente, (rut_residente,))

#     if resultado_residente is None or len(resultado_residente) == 0:
#         raise ValueError(f"Error al verificar el residente. No se obtuvo respuesta de la base de datos.")
    
#     if resultado_residente[0][0] > 0:
#         raise ValueError(f"Ya existe un residente con el RUT {rut_residente}.")
    
#     # Si el residente no existe, insertamos en la tabla residente
#     consulta_insertar_residente = """
#     INSERT INTO residente (rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente)
#     VALUES (%s, %s, %s, %s, %s, %s, %s)
#     """
    
#     try:
#         # Ejecutamos la inserción del residente
#         ejecutar_consulta(consulta_insertar_residente, (rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente))

#         # Confirmar la transacción
#         conn.commit()  # Confirmamos la transacción
#         print(f"Residente {rut_residente} insertado correctamente en la tabla residente.")

#         # Ahora, si se proporcionó una patente, asociamos el vehículo
#         if patente_vehiculo:
#             consulta_existente_vehiculo = """
#             SELECT COUNT(*) FROM vehiculo WHERE patente_vehiculo = %s
#             """
#             resultado_vehiculo = ejecutar_consulta(consulta_existente_vehiculo, (patente_vehiculo,))
            
#             if resultado_vehiculo is None or len(resultado_vehiculo) == 0:
#                 raise ValueError(f"Error al verificar la patente del vehículo. No se obtuvo respuesta de la base de datos.")
            
#             if resultado_vehiculo[0][0] > 0:
#                 raise ValueError(f"Ya existe un vehículo con la patente {patente_vehiculo} asociado a otro residente.")
            
#             # Insertar en la tabla vehiculo, asociando el vehículo al rut_residente
#             consulta_insertar_vehiculo = """
#             INSERT INTO vehiculo (patente_vehiculo, residente_rut_residente)
#             VALUES (%s, %s)
#             """
#             ejecutar_consulta(consulta_insertar_vehiculo, (patente_vehiculo, rut_residente))
#             print(f"Vehículo con patente {patente_vehiculo} asociado correctamente al residente {rut_residente}.")
    
#     except Exception as e:
#         # Revertir cualquier cambio si ocurre un error
#         conn.rollback()
#         print(f"Error al ejecutar consulta: {e}")
#         raise ValueError(f"Error al insertar el residente o el vehículo: {str(e)}")
    
#     finally:
#         conn.close()  # Cerrar la conexión al final



def insertar_residente(rut, dv, nombre, apellido, fecha_nac, telefono, no_depto, patente):
    # Conectar a la base de datos
    conn = conectar()
    cursor = conn.cursor()

    try:
        # Insertar en la tabla residente
        cursor.execute("""
            INSERT INTO residente (rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (rut, dv, nombre, apellido, fecha_nac, telefono, no_depto))

        # Insertar en la tabla vehiculo
        cursor.execute("""
            INSERT INTO vehiculo (patente_vehiculo, residente_rut_residente)
            VALUES (%s, %s)
        """, (patente, rut))

        # Confirmar cambios
        conn.commit()

    except Exception as e:
        conn.rollback()  # Deshacer cambios en caso de error
        raise e  # Propagar el error para manejarlo en residentes.py

    finally:
        cursor.close()
        conn.close()
        

def obtener_residente_por_rut(rut):
    conexion = conectar()  # Asegúrate de tener la conexión configurada
    cursor = conexion.cursor()
    consulta = """
    SELECT rut_residente, dv_residente, nombre_residente, apellido_residente, 
           fec_nac_residente, telefono_residente, no_depto_residente
    FROM residente
    WHERE rut_residente = %s;
    """
    try:
        cursor.execute(consulta, (rut,))
        residente = cursor.fetchone()
        return residente
    except Exception as e:
        print("Error al obtener residente por RUT:", e)
        return None
    finally:
        cursor.close()
        conexion.close()

def actualizar_residente(rut, telefono, no_depto):
    conexion = conectar()  # Asegúrate de tener la conexión a la base de datos configurada
    cursor = conexion.cursor()

    consulta = """
    UPDATE residente
    SET telefono_residente = %s, no_depto_residente = %s
    WHERE rut_residente = %s;
    """
    try:
        cursor.execute(consulta, (telefono, no_depto, rut))
        conexion.commit()
        return True
    except Exception as e:
        print("Error al actualizar residente:", e)
        conexion.rollback()
        return False
    finally:
        cursor.close()
        conexion.close()








# Función para obtener los datos de un residente por su RUT
# def obtener_residente_por_rut(rut):
#     consulta = "SELECT * FROM residentes WHERE rut = %s"
#     conexion = conectar()
#     cursor = conexion.cursor()
#     cursor.execute(consulta, (rut,))
#     residente = cursor.fetchone()
#     cursor.close()
#     conexion.close()
#     return residente

# Función para actualizar los datos de un residente
# def actualizar_residente(rut, nuevos_datos):
#     # Construir la consulta UPDATE dinámica basada en los campos a actualizar
#     # ... (ejemplo: actualizar nombre y apellido)
#     consulta = """
#     UPDATE residentes
#     SET nombre = %s, apellido = %s
#     WHERE rut = %s
#     """
#     ejecutar_consulta(consulta, (nuevos_datos['nombre'], nuevos_datos['apellido'], rut))

# Función para eliminar un residente
# def eliminar_residente(rut):
#     consulta = "DELETE FROM residentes WHERE rut = %s"
#     ejecutar_consulta(consulta, (rut,))