import tkinter as tk
from tkinter import ttk
import psycopg2  # Asegúrate de tener esta biblioteca instalada

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Reportes")
ventana.geometry("1000x500")  # Ajustar el tamaño de la ventana

# Crear variables para los tipos de reportes
tipo_reporte = tk.StringVar()

# Función para conectarse a la base de datos
def conectar_db():
    try:
        conexion = psycopg2.connect(
            host="localhost",
            database="autovision",
            user="postgres",
            password="root"
        )
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Función para obtener datos de residentes y multados
def obtener_datos():
    try:
        conn = conectar_db()
        if conn is None:
            return [], {}
        
        cursor = conn.cursor()

        # Consulta para obtener datos de residentes
        cursor.execute("SELECT rut_visita_historica, dv_visita_historica, nombre_visita_historica, apellido_visita_historica, no_depto_visita_historica, patente_visita_historica, momento_ingreso_historico, momento_salida_historico, visita_rut_visita FROM visita_historico")
        datos_residentes = cursor.fetchall()

        # Supongamos que en tu base de datos hay una forma de determinar si está multado
        # Esto es un ejemplo, ajusta según tu lógica real
        cursor.execute("SELECT rut_visita_historica, true AS multado FROM visitas_multadas")  # Ajusta esta consulta
        datos_multados = cursor.fetchall()

        # Cerrar la conexión
        cursor.close()
        conn.close()

        # Transformar los datos a formato (RUT, Nombre, Apellido, Depto, Patente, Ingreso, Multado)
        multados_dict = {registro[0]: True for registro in datos_multados}  # Asume que el RUT es el primer campo
        return datos_residentes, multados_dict

    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return [], {}

# Cargar los datos de la base de datos
datos_residentes, multados_dict = obtener_datos()

# Crear el marco para centrar el Treeview y su barra de desplazamiento 
frame = ttk.Frame(ventana, width=700, height=200)
frame.grid(row=3, columnspan=5, padx=(200), pady=(100))
frame.grid_propagate(False)

# Crear el Treeview para mostrar resultados 
tree = ttk.Treeview(frame, show="headings", height=10)
tree.pack(side='left', fill='both', expand=True)

# Crear una barra de desplazamiento vertical 
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)  
scrollbar.pack(side='right', fill='y')  
tree.configure(yscrollcommand=scrollbar.set)

# Función para configurar columnas específicas
def configurar_columnas():
    tree["columns"] = ("RUT", "Nombre", "Apellido", "Depto", "Patente", "Ingreso", "Multado")
    tree.heading("RUT", text="RUT")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Apellido", text="Apellido")
    tree.heading("Depto", text="Depto")
    tree.heading("Patente", text="Patente")
    tree.heading("Ingreso", text="Fecha Ingreso")
    tree.heading("Multado", text="Multado")

    # Ajustar las columnas para que se estiren automáticamente
    for col in tree["columns"]:
        tree.column(col, width=100, stretch=True)

# Función para cargar datos en el Treeview
def cargar_datos(datos):
    configurar_columnas()
    limpiar_tabla()
    for registro in datos:
        rut = registro[0]
        multado = multados_dict.get(rut, False)  # Determina si está multado
        tree.insert("", "end", values=registro + (multado,))  # Añade el estado de multado

# Función para limpiar la tabla antes de insertar nuevos datos
def limpiar_tabla():
    for row in tree.get_children():
        tree.delete(row)

# Función para manejar la selección del tipo de reporte
def seleccionar_reporte(event=None):
    seleccion = tipo_reporte.get()
    if seleccion == "Reporte Residentes":
        cargar_datos(datos_residentes)
    elif seleccion == "Reporte Multados":
        cargar_datos(datos_multados)  # Asumiendo que quieres cargar datos multados de la misma manera

# Crear un Label y un OptionMenu para seleccionar el tipo de reporte
label_seleccion = tk.Label(ventana, text="Selecciona el tipo de reporte:")
label_seleccion.grid(row=0, column=0, padx=(50, 10), pady=(20, 10))

opciones_reporte = ["Reporte Residentes", "Reporte Multados"]
menu_opciones = ttk.OptionMenu(ventana, tipo_reporte, opciones_reporte[0], *opciones_reporte, command=seleccionar_reporte)
menu_opciones.grid(row=0, column=1, padx=(10, 50), pady=(20, 10))

# Botón para generar el reporte manualmente
boton_generar = ttk.Button(ventana, text="Generar Reporte", command=seleccionar_reporte)
boton_generar.grid(row=1, column=1, padx=(10, 50), pady=(10, 20))

# Inicializar con los datos de Residentes por defecto
tipo_reporte.set("Reporte Residentes")
cargar_datos(datos_residentes)

# Iniciar el loop principal de la ventana
ventana.mainloop()
