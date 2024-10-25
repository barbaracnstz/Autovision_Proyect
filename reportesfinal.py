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
    cursor.close()  # Cerrar el cursor
    return datos

# Función para actualizar el Treeview según el tipo de reporte
def actualizar_treeview(tipo_reporte):
    conn = conectar_base_datos()
    if conn:
        datos = obtener_datos(tipo_reporte, conn)

        # Limpiar el Treeview antes de agregar nuevos datos
        for i in tree.get_children():
            tree.delete(i)

        # Configurar las columnas según el tipo de reporte
        if tipo_reporte == "Multados":
            tree["columns"] = ('rut visita', 'dv', 'nombre_visita_historica', 
                               'apellido_visita_historica', 'nro departamento', 
                               'patente_visita_historica', 
                               'momento_ingreso_historico', 
                               'momento_salida_historico', 
                               'visita_rut_visita')
            for col in tree["columns"]:
                tree.heading(col, text=col)

            # Anchos de columnas para multados
            tree.column("rut visita", width=80)
            tree.column("dv", width=50)
            tree.column("nombre_visita_historica", width=80)
            tree.column("apellido_visita_historica", width=80)
            tree.column("nro departamento", width=50)
            tree.column("patente_visita_historica", width=80)
            tree.column("momento_ingreso_historico", width=80)
            tree.column("momento_salida_historico", width=80)
            tree.column("visita_rut_visita", width=80)

        elif tipo_reporte == "Residentes":
            tree["columns"] = ('rut', 'dv','nombre', 'apellido', 'departamento','departamento')
            for col in tree["columns"]:
                tree.heading(col, text=col)

            # Anchos de columnas para residentes
            tree.column("rut", width=60)
            tree.column("dv", width=30)
            tree.column("nombre", width=50)
            tree.column("apellido", width=50)
            tree.column("departamento", width=50)
            tree.column("departamento", width=50)

        # Agregar los nuevos datos al Treeview
        for row in datos:
            tree.insert('', 'end', values=row)

        conn.close()

# Crear la ventana principal
root = tk.Tk()
root.title("Sistema de Reportes")
root.geometry("600x400")

# Crear un Frame para el Treeview
frame = tk.Frame(root, width=500, height=300)
frame.place(relx=0.5, rely=0.5, anchor='center')  # Centrar el frame en la ventana

# Crear el Treeview
tree = ttk.Treeview(frame, show='headings')
tree.pack(fill='both', expand=True)

# Crear un menú desplegable para seleccionar el tipo de reporte
tipo_reporte_var = tk.StringVar()
tipo_reporte_var.set("Multados")  # Valor por defecto

# Crear un label para el título
titulo_label = tk.Label(root, text="REPORTES", font=("Helvetica", 16))
titulo_label.pack(pady=10)  # Espacio arriba y abajo del título

# Menú desplegable
tipo_reporte_menu = ttk.Combobox(root, textvariable=tipo_reporte_var, values=["Multados", "Residentes"])
tipo_reporte_menu.pack(pady=10)  # Agregar un poco de espacio

# Botón para actualizar los datos
boton_actualizar = tk.Button(root, text="Buscar", command=lambda: actualizar_treeview(tipo_reporte_var.get()))
boton_actualizar.pack(pady=10)  # Agregar un poco de espacio

# Llamada inicial para cargar los datos
actualizar_treeview("Multados")

root.mainloop()
