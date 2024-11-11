import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import psycopg2
from datetime import datetime
import openpyxl
from PIL import Image, ImageTk

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

# Función para actualizar el Treeview
def actualizar_treeview(tipo_reporte, fecha_desde=None, fecha_hasta=None):
    if fecha_desde and fecha_hasta:
        datos = obtener_datos_entre_fechas(tipo_reporte, fecha_desde, fecha_hasta)
    else:
        datos = obtener_datos(tipo_reporte)
    
    # Limpiar el Treeview antes de agregar nuevos datos
    for i in tree.get_children():
        tree.delete(i)
    
    # Configurar las columnas según el tipo de reporte
    if tipo_reporte == "Multados":
        columns = ('Rut Residente', 'Nombre', 'Apellido','nro departamento','rut visita', 'Nombre Visita', 'Apellido Visita' 
                   , 'Patente Visita', 
                   'Momento Ingreso', 'Momento Salida')
    elif tipo_reporte == "Residentes":
        columns = ('rut_residente', 'dv_residente', 'nombre_residente', 'apellido_residente', 
                   'fec_nac_residente', 'telefono_residente', 'no_depto_residente', 
                   'patente_vehiculo')
    elif tipo_reporte == "Visitas Diarias":
        columns = ('RUT VISITA', 'NOMBRE', 'APELLIDO', 'DEPARTAMENTO', 
                   'PATENTE')

    # Configurar el Treeview con las nuevas columnas
    tree['columns'] = columns
    for col in columns:
        tree.heading(col, text=col)  # Establecer los encabezados
        tree.column(col, width=70)  # Establecer un ancho fijo para cada columna

    # Agregar los nuevos datos al Treeview
    if datos:
        for row in datos:
            tree.insert('', 'end', values=row)
    else:
        messagebox.showinfo("Sin resultados", "No se encontraron datos en el rango de fechas seleccionado.")

# Función para filtrar los datos
def filtrar_datos():
    tipo_reporte = tipo_reporte_var.get()
    fecha_desde = datetime.combine(fecha_desde_entry.get_date(), datetime.min.time())
    fecha_hasta = datetime.combine(fecha_hasta_entry.get_date(), datetime.max.time())

    actualizar_treeview(tipo_reporte, fecha_desde, fecha_hasta)

# Función para generar el reporte en Excel
def generar_reporte_excel():
    # Obtener los datos del Treeview
    datos = []
    for row in tree.get_children():
        datos.append(tree.item(row)['values'])

    if not datos:
        messagebox.showwarning("Sin datos", "No hay datos para exportar.")
        return

    # Preguntar al usuario dónde guardar el archivo
    ruta_archivo = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                  filetypes=[("Archivos Excel", "*.xlsx"),
                                                             ("Todos los archivos", "*.*")])
    if not ruta_archivo:
        return  # Si el usuario cancela, no hacemos nada

    # Crear un libro de trabajo y una hoja
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.title = "Reporte"

    # Escribir los encabezados
    columnas = tree['columns']
    hoja.append(columnas)

    # Escribir los datos
    for fila in datos:
        hoja.append(fila)

    # Guardar el archivo
    libro.save(ruta_archivo)
    messagebox.showinfo("Éxito", "Reporte generado correctamente.")

# Crear la ventana principal revisar
root = tk.Tk()
root.title("Sistema de Reportes")
root.geometry("1920x1020")  # Ajusta el tamaño según tus necesidades

# Cargar la imagen de fondo
fondo_img = Image.open("fondo.png")
fondo_img = fondo_img.resize((1600, 920), Image.LANCZOS)  # Cambiar a LANCZOS
fondo_photo = ImageTk.PhotoImage(fondo_img)

# Crear un label para la imagen de fondo
label_fondo = tk.Label(root, image=fondo_photo)
label_fondo.place(relwidth=1, relheight=1)  # Ajustar a todo el fondo

# Crear un menú desplegable para seleccionar el tipo de reporte
tipo_reporte_var = tk.StringVar()
tipo_reporte_var.set("Multados")  # Valor por defecto

# Crear un label para el título
titulo_label = tk.Label(root, text="REPORTES", font=("Helvetica", 16), bg='white')  # Cambiar bg según la imagen
titulo_label.pack(pady=10)

titulo_tipo = tk.Label(root, text="Seleccione el tipo de reporte:", bg='white')
titulo_tipo.pack(pady=5)
tipo_reporte_menu = ttk.Combobox(root, textvariable=tipo_reporte_var, values=["Multados", "Residentes" ,"Visitas Diarias"])
tipo_reporte_menu.pack(pady=5)

# Crear entradas de fecha
fecha_desde_label = tk.Label(root, text="Fecha Desde:", bg='white')  # Cambiar bg según la imagen
fecha_desde_label.pack(pady=5)
fecha_desde_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
fecha_desde_entry.pack(pady=5)

fecha_hasta_label = tk.Label(root, text="Fecha Hasta:", bg='white')  # Cambiar bg según la imagen
fecha_hasta_label.pack(pady=5)
fecha_hasta_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
fecha_hasta_entry.pack(pady=5)

# Botón para filtrar los datos
boton_filtrar = tk.Button(root, text="Filtrar", command=filtrar_datos)
boton_filtrar.pack(pady=5)



# Crear el Treeview
tree = ttk.Treeview(root, show='headings', height=15)  # Ajusta la altura según tus necesidades
tree.pack(fill='x', padx=50, pady=50)  # Ajustar para que no ocupe todo el ancho

# Botón para generar el reporte en Excel
boton_generar_excel = tk.Button(root, text="Generar Reporte", command=generar_reporte_excel)
boton_generar_excel.pack(pady=5)
# Llamada inicial para cargar los datos
actualizar_treeview("Multados")

# Bind the combobox selection change to update the Treeview
tipo_reporte_menu.bind("<<ComboboxSelected>>", lambda event: actualizar_treeview(tipo_reporte_var.get()))

root.mainloop()
