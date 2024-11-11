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
def insertar_residente(rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente, patente_vehiculo):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Insertar residente
            query_residente = """
            INSERT INTO residente (rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query_residente, (rut_residente, dv_residente, nombre_residente, apellido_residente, fec_nac_residente, telefono_residente, no_depto_residente))
            
            # Insertar vehículo si se proporciona patente
            if patente_vehiculo:
                query_vehiculo = """
                INSERT INTO vehiculo (patente_vehiculo, residente_rut_residente)
                VALUES (%s, %s);
                """
                cursor.execute(query_vehiculo, (patente_vehiculo, rut_residente))
            
            # Commit y cierre de conexión
            conexion.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al insertar residente o vehículo: {e}")
        finally:
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

###############################################REPORTESssssssssssssssssssssss
# Función para establecer la conexión a la base de datos
def conectar_base_datos():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="autovision",
            user="postgres",
            password="root"
        )
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error al conectar a la base de datos:", error)
        return None

# Función para obtener los datos según el tipo de reporte
def obtener_datos(tipo_reporte):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    
    if tipo_reporte == "Multados":
        cursor.execute("""
                    SELECT r.rut_residente,
                            r.nombre_residente,
                            r.apellido_residente,
                            vh.no_depto_visita_historica,
                            vh.rut_visita_historica,
                            vh.nombre_visita_historica,
                            vh.apellido_visita_historica,
                            vh.patente_visita_historica,
                            vh.momento_ingreso_historico,
                            vh.momento_salida_historico
                    FROM visita_historico vh
                    JOIN visita v ON vh.visita_rut_visita = v.rut_visita
                    JOIN residente r ON v.residente_rut_residente = r.rut_residente
                    WHERE vh.multado = TRUE;""")
    elif tipo_reporte == "Residentes":
        cursor.execute("""
            SELECT r.rut_residente, r.dv_residente, r.nombre_residente, r.apellido_residente, 
                   r.fec_nac_residente, r.telefono_residente, r.no_depto_residente, 
                   v.patente_vehiculo
            FROM residente r
            LEFT JOIN vehiculo v ON r.rut_residente = v.residente_rut_residente
        """)
    elif tipo_reporte == "Visitas Diarias":
        cursor.execute("""
            SELECT rut_visita_historica,nombre_visita_historica,apellido_visita_historica,no_depto_visita_historica AS departamento,
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
    conn = conectar_base_datos()
    cursor = conn.cursor()
    
    if tipo_reporte == "Multados":
        cursor.execute("""
            SELECT r.rut_residente,
                            r.nombre_residente,
                            r.apellido_residente,
                            vh.no_depto_visita_historica,
                            vh.rut_visita_historica,
                            vh.nombre_visita_historica,
                            vh.apellido_visita_historica,
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
            SELECT r.rut_residente, r.dv_residente, r.nombre_residente, r.apellido_residente, 
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