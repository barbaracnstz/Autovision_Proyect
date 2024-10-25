import tkinter as tk
from tkinter import ttk
import psycopg2

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
        print("Error al conectar a la base de datos", error)
        return None

# Función para obtener los datos según el tipo de reporte
def obtener_datos(tipo_reporte, conn):
    cursor = conn.cursor()
    if tipo_reporte == "Multados":
        cursor.execute("SELECT * FROM visita_historico WHERE multado = True")
    elif tipo_reporte == "Residentes":
        cursor.execute("SELECT * FROM residente")
    else:
        print("Tipo de reporte inválido")
    datos = cursor.fetchall()
    return datos

# Función para actualizar el Treeview
def actualizar_treeview(tipo_reporte):
    conn = conectar_base_datos()
    if conn:
        datos = obtener_datos(tipo_reporte, conn)
        # Limpiar el Treeview antes de agregar nuevos datos
        for i in tree.get_children():
            tree.delete(i)
        # Agregar los nuevos datos al Treeview
        for row in datos:
            tree.insert('', 'end', values=row)
        conn.close()

# Crear la ventana principal
root = tk.Tk()
root.title("Sistema de Reportes")

# Crear el Treeview
columns = ('rut visita', 'dv', 'nombre_visita_historica', 'apellido_visita_historica', 'nro departamento', 'patente_visita_historica', 'momento_ingreso_historico', 'momento_salida_historico', 'visita_rut_visita')
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)

# Configurar el ancho de las columnas
tree.column("rut visita", width=100)
tree.column("dv", width=80)
tree.column("nombre_visita_historica", width=150)
tree.column("apellido_visita_historica", width=150)
tree.column("nro departamento", width=70)
tree.column("nombre_visita_historica", width=150)

# Crear un menú desplegable para seleccionar el tipo de reporte
tipo_reporte_var = tk.StringVar()
tipo_reporte_var.set("Multados")  # Valor por defecto
# Crear un label para el título
titulo_label = tk.Label(root, text="REPORTES", font=("Helvetica", 16))
titulo_label.pack(pady=10)  # Agregamos un poco de espacio arriba y abajo del título
tipo_reporte_menu = ttk.Combobox(root, textvariable=tipo_reporte_var, values=["Multados", "Residentes"])
tipo_reporte_menu.pack()

# Botón para actualizar los datos
boton_actualizar = tk.Button(root, text="Buscar", command=lambda: actualizar_treeview(tipo_reporte_var.get()))
boton_actualizar.pack()

# Mostrar el Treeview
tree.pack(fill='both', expand=True)

# Llamada inicial para cargar los datos
actualizar_treeview("Multados")

root.mainloop()