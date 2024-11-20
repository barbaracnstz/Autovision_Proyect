import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import openpyxl
from PIL import Image, ImageTk
from bd import obtener_datos,obtener_datos_entre_fechas, conectar  # Importar la conexión desde bd.py
from datetime import datetime
from menu import crear_menu
import customtkinter as ctk

# Función para abrir la ventana de reportes
def abrir_ventana_reportes():
    root = tk.Toplevel()  # Crear una nueva ventana secundaria
    root.title("Sistema de Reportes")
    root.geometry("1920x1020")  # Ajusta el tamaño según tus necesidades
    
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
            columns = ('RUT RESIDENTE', 'NOMBRE COMPLETO','DEPARTAMENTO','RUT VISITA', 'NOMBRE COMPLETO VISITA' 
                    , 'PATENTE VISITA', 
                    'Momento Ingreso', 'Momento Salida')
        elif tipo_reporte == "Residentes":
            columns = ('RUT RESIDENTE', 'NOMBRE COMPLETO', 
                   'FECHA NACIMIENTO', 'TELEFONO', 'DEPARTAMENTO', 
                   'PATENTE DEL VEHICULO')
        elif tipo_reporte == "Visitas Diarias":
            columns = ('RUT VISITA', 'NOMBRE COMPLETO', 'DEPARTAMENTO', 
                    'PATENTE')


        # Configurar el Treeview con las nuevas columnas
        tree['columns'] = columns
        for col in columns:
            tree.heading(col, text=col)  # Establecer los encabezados
            tree.column(col, width=70 ,anchor='center')  # Establecer un ancho fijo para cada columna

        # Agregar los nuevos datos al Treeview
        if datos:
            for row in datos:
                tree.insert('', 'end', values=row)
        else:
            messagebox.showinfo("Sin resultados", "No se encontraron datos.")

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
    
    # Crear el menú
    crear_menu(root)

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
    boton_filtrar = ctk.CTkButton(
        root,fg_color="white",
        text="Filtrar",
        command=filtrar_datos,
        border_color="black",  # Borde negro
        border_width=2,        # Ancho del borde
        text_color="black",    # Color de la letra en negro
        hover_color="gray",    # Color cuando se pasa el ratón por encima
        width=100,             # Ancho del botón
        height=25              # Alto del botón
    )
    boton_filtrar.pack(pady=5)



    # Crear el Treeview
    tree = ttk.Treeview(root, show='headings', height=15)  # Ajusta la altura según tus necesidades
    tree.pack(fill='x', padx=50, pady=50)  # Ajustar para que no ocupe todo el ancho

    # Botón para generar el reporte en Excel
    boton_generar_excel = ctk.CTkButton(
        root, 
        text="Generar Reporte", 
        command=generar_reporte_excel, 
        fg_color="#28a745",  # Color verde de fondo (usando código hex)
        hover_color="#218838",  # Color verde más oscuro cuando pasa el mouse (efecto hover)
        width=200,  # Ancho del botón
        height=40,  # Altura del botón
        font=("Arial", 16, "bold"),  # Fuente del texto
        corner_radius=10  # Bordes redondeados
    )

    # Empacar el botón en la ventana
    boton_generar_excel.pack(pady=5)
    # Llamada inicial para cargar los datos
    actualizar_treeview("Multados")

    # Bind the combobox selection change to update the Treeview
    tipo_reporte_menu.bind("<<ComboboxSelected>>", lambda event: actualizar_treeview(tipo_reporte_var.get()))

    root.mainloop()
