import psycopg2
from tkinter import messagebox 


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
            password="root"
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
def eliminar_registro(rut):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()

            # Eliminar el vehículo asociado al residente (si existe)
            query_vehiculo = """
            DELETE FROM vehiculo
            WHERE residente_rut_residente = %s;
            """
            cursor.execute(query_vehiculo, ((rut),))

            # Eliminar el residente de la tabla residente
            query_residente = """
            DELETE FROM residente
            WHERE rut_residente = %s;
            """
            cursor.execute(query_residente, ((rut),))

            # Confirmar cambios
            conexion.commit()

            # Cerrar cursor
            cursor.close()

            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "El registro del residente ha sido eliminado correctamente.")

        except Exception as e:
            print(f"Error al eliminar residente: {e}")
            messagebox.showerror("Error", "Hubo un problema al eliminar el registro del residente.")
        finally:
            conexion.close()

###############################################REPORTES
# Función para establecer la conexión a la base de datos
# def conectar_base_datos():
#     try:
#         conn = psycopg2.connect(
#             host="localhost",
#             database="autovision",
#             user="postgres",
#             password="root"
#         )
#         return conn
#     except (Exception, psycopg2.Error) as error:
#         print("Error al conectar a la base de datos:", error)
#         return None

# Función para obtener los datos según el tipo de reporte
def obtener_datos(tipo_reporte):
    conn = conectar()
    cursor = conn.cursor()
    
    if tipo_reporte == "Multados":
        cursor.execute("""
                    SELECT r.rut_residente,
                            CONCAT(r.nombre_residente,' ',
                            r.apellido_residente),
                            vh.no_depto_visita_historica,
                            vh.rut_visita_historica,
                            CONCAT(vh.nombre_visita_historica,' ',
                            vh.apellido_visita_historica),
                            vh.patente_visita_historica,
                            vh.momento_ingreso_historico,
                            vh.momento_salida_historico
                    FROM visita_historico vh
                    JOIN visita v ON vh.visita_rut_visita = v.rut_visita
                    JOIN residente r ON v.residente_rut_residente = r.rut_residente
                    WHERE vh.multado = TRUE;""")
    elif tipo_reporte == "Residentes":
        cursor.execute("""
            SELECT CONCAT(r.rut_residente, '-', r.dv_residente), CONCAT(r.nombre_residente, ' ', r.apellido_residente), 
                   r.fec_nac_residente, r.telefono_residente, r.no_depto_residente, 
                   v.patente_vehiculo
            FROM residente r
            LEFT JOIN vehiculo v ON r.rut_residente = v.residente_rut_residente
        """)
    elif tipo_reporte == "Visitas Diarias":
        cursor.execute("""
            SELECT rut_visita_historica,CONCAT(nombre_visita_historica,' ',apellido_visita_historica),no_depto_visita_historica AS departamento,
                   patente_visita_historica
            FROM visita_historico
            WHERE DATE(momento_ingreso_historico) = CURRENT_DATE;
        """)
    else:
        print("Tipo de reporte inválido")
        return []
    
    datos = cursor.fetchall()
    cursor.close()  # Cerrar el cursor
    return datos

# Función para obtener los datos entre fechas
def obtener_datos_entre_fechas(tipo_reporte, fecha_desde, fecha_hasta):
    conn = conectar()
    cursor = conn.cursor()
    
    if tipo_reporte == "Multados":
        cursor.execute("""
            SELECT r.rut_residente,
                            CONCAT(r.nombre_residente,' ',
                            r.apellido_residente),
                            vh.no_depto_visita_historica,
                            vh.rut_visita_historica,
                            CONCAT(vh.nombre_visita_historica,' ',
                            vh.apellido_visita_historica),
                            vh.patente_visita_historica,
                            vh.momento_ingreso_historico,
                            vh.momento_salida_historico
                    FROM visita_historico vh
                    JOIN visita v ON vh.visita_rut_visita = v.rut_visita
                    JOIN residente r ON v.residente_rut_residente = r.rut_residente
                    WHERE vh.multado = TRUE
            AND momento_ingreso_historico >= %s 
            AND momento_ingreso_historico <= %s
        """, (fecha_desde, fecha_hasta))
    elif tipo_reporte == "Residentes":
        cursor.execute("""
            SELECT CONCAT(r.rut_residente, '-', r.dv_residente), CONCAT(r.nombre_residente, ' ', r.apellido_residente), 
                   r.fec_nac_residente, r.telefono_residente, r.no_depto_residente, 
                   v.patente_vehiculo
            FROM residente r
            LEFT JOIN vehiculo v ON r.rut_residente = v.residente_rut_residente
            WHERE r.fecha_registro >= %s AND r.fecha_registro <= %s
        """, (fecha_desde, fecha_hasta))
    else:
        print("Tipo de reporte inválido")
        return []
    
    datos = cursor.fetchall()
    cursor.close()  # Cerrar el cursor
    return datos






