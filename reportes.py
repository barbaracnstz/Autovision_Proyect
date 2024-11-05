import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import openpyxl
from PIL import Image, ImageTk
from bd import conectar  # Importar la conexión desde bd.py
from datetime import datetime
from menu import crear_menu


# Función para abrir la ventana de reportes
def abrir_ventana_reportes():
    root = tk.Toplevel()  # Crear una nueva ventana secundaria
    root.title("Sistema de Reportes")
    root.geometry("1920x1020")  # Ajusta el tamaño según tus necesidades
    
    # Crear el menú
    crear_menu(root)

    # Crear un menú desplegable para el tipo de reporte
    tipo_reporte_var = tk.StringVar(value="Multados")
    tipo_reporte_menu = ttk.Combobox(root, textvariable=tipo_reporte_var, values=["Multados", "Residentes"])
    tipo_reporte_menu.pack(pady=5)

    # Entradas de fecha
    fecha_desde_label = tk.Label(root, text="Fecha Desde:")
    fecha_desde_label.pack(pady=5)
    fecha_desde_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
    fecha_desde_entry.pack(pady=5)

    fecha_hasta_label = tk.Label(root, text="Fecha Hasta:")
    fecha_hasta_label.pack(pady=5)
    fecha_hasta_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
    fecha_hasta_entry.pack(pady=5)

    # Botón para filtrar datos
    boton_filtrar = tk.Button(root, text="Filtrar", command=lambda: filtrar_datos(tipo_reporte_var, fecha_desde_entry, fecha_hasta_entry))
    boton_filtrar.pack(pady=5)

    # Treeview
    tree = ttk.Treeview(root, show='headings', height=15)
    tree.pack(fill='x', padx=50, pady=50)

    # Botón para exportar a Excel
    boton_generar_excel = tk.Button(root, text="Generar Reporte", command=lambda: generar_reporte_excel(tree))
    boton_generar_excel.pack(pady=5)

    # Función para actualizar el Treeview
    def actualizar_treeview(tipo_reporte, fecha_desde=None, fecha_hasta=None):
        if fecha_desde and fecha_hasta:
            datos = obtener_datos_entre_fechas(tipo_reporte, fecha_desde, fecha_hasta)
        else:
            datos = obtener_datos(tipo_reporte)

        tree.delete(*tree.get_children())  # Limpiar el Treeview

        # Configurar columnas y encabezados según el tipo de reporte
        columns = ('rut_residente', 'dv_residente', 'nombre_residente', 'apellido_residente', 'patente_vehiculo') \
                  if tipo_reporte == "Residentes" else ('rut_visita', 'momento_ingreso_historico', 'multado')
        tree['columns'] = columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)

        for row in datos:
            tree.insert('', 'end', values=row)

    # Obtención de datos (usando conexión desde bd.py)
    def obtener_datos(tipo_reporte):
        conn = conectar()
        cursor = conn.cursor()
        if tipo_reporte == "Multados":
            cursor.execute("SELECT * FROM visita_historico WHERE multado = True")
        elif tipo_reporte == "Residentes":
            cursor.execute("""
                SELECT r.rut_residente, r.dv_residente, r.nombre_residente, r.apellido_residente, 
                       r.fec_nac_residente, r.telefono_residente, r.no_depto_residente, 
                       v.patente_vehiculo
                FROM residente r
                LEFT JOIN vehiculo v ON r.rut_residente = v.residente_rut_residente
            """)
        datos = cursor.fetchall()
        cursor.close()
        return datos

    tipo_reporte_menu.bind("<<ComboboxSelected>>", lambda event: actualizar_treeview(tipo_reporte_var.get()))
    actualizar_treeview("Multados")  # Llamada inicial
    root.mainloop()

# Crear función para generar reporte en Excel
def generar_reporte_excel(tree):
    datos = [tree.item(row)['values'] for row in tree.get_children()]
    if not datos:
        messagebox.showwarning("Sin datos", "No hay datos para exportar.")
        return
    ruta_archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos Excel", "*.xlsx")])
    if not ruta_archivo:
        return
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.title = "Reporte"
    hoja.append(tree['columns'])  # Encabezados
    for fila in datos:
        hoja.append(fila)
    libro.save(ruta_archivo)
    messagebox.showinfo("Éxito", "Reporte generado correctamente.")
