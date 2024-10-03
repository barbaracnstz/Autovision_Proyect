import psycopg2
from tkinter import Tk, Label, Button, Listbox, END
from datetime import datetime

# Conectar a la base de datos PostgreSQL
def conectar_db():
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

# Obtener el reporte diario de visitas
def obtener_reporte_diario():
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Filtrar las visitas del día actual
    hoy = datetime.now().date()
    query = """
        SELECT rut_visita_historica, nombre_visita_historica, apellido_visita_historica, 
               no_depto_visita_historica, patente_visita_historica, momento_ingreso_historico
        FROM visita_historico
        WHERE DATE(momento_ingreso_historico) = %s
    """
    cursor.execute(query, (hoy,))
    visitas = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return visitas

# Función para mostrar el reporte en la interfaz
def mostrar_reporte():
    lista_visitas.delete(0, END)  # Limpiar la lista
    visitas = obtener_reporte_diario()
    
    if visitas:
        for visita in visitas:
            lista_visitas.insert(END, f"RUT: {visita[0]}, Nombre: {visita[1]} {visita[2]}, Depto: {visita[3]}, Patente: {visita[4]}, Ingreso: {visita[5]}")
    else:
        lista_visitas.insert(END, "No hay visitas registradas hoy.")

# Crear la interfaz gráfica con Tkinter
ventana = Tk()
ventana.title("Reporte Diario de Visitas")

# Etiqueta de título
titulo = Label(ventana, text="Reporte Diario de Visitas", font=("Arial", 16))
titulo.pack(pady=10)

# Botón para generar el reporte
boton_reporte = Button(ventana, text="Generar Reporte", command=mostrar_reporte)
boton_reporte.pack(pady=10)

# Lista donde se mostrarán las visitas
lista_visitas = Listbox(ventana, width=100, height=20)
lista_visitas.pack(pady=10)

# Ejecutar la interfaz
ventana.mainloop()