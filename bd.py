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

