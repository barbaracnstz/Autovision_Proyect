import psycopg2
import tkinter as tk
from tkinter import ttk
from tkinter import Tk, Label, Button, Radiobutton, StringVar, END
from tkcalendar import DateEntry
from tkinter import ttk, filedialog
from datetime import datetime
from openpyxl import Workbook

def abrir_ventana_reportes():
    ventana_reportes = tk.Toplevel()  # Utiliza tk en minúsculas para acceder a Toplevel
    ventana_reportes.title("Ventana de Reportes")
    
    # 1. Función para conectarse a la base de datos PostgreSQL
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

    # 2. Función para obtener visitas multadas entre fechas
    def obtener_multados_fechas(desde, hasta):
        try:
            conexion = conectar_db()
            if not conexion:
                return []

            cursor = conexion.cursor()

            query = """
                SELECT rut_visita_historica, nombre_visita_historica, apellido_visita_historica, 
                    no_depto_visita_historica, patente_visita_historica, momento_ingreso_historico
                FROM visita_historico
                WHERE momento_ingreso_historico >= %s AND momento_ingreso_historico < %s + interval '1 day'
                AND multado = TRUE
            """
            cursor.execute(query, (desde, hasta))
            multados = cursor.fetchall()

            cursor.close()
            conexion.close()
            return multados
        except Exception as e:
            print(f"Error en la consulta SQL: {e}")
            return []

    # 3. Función para obtener residentes (actualmente sin filtro de fecha)
    def obtener_residentes_fechas():
        try:
            conexion = conectar_db()
            if not conexion:
                return []

            cursor = conexion.cursor()

            query = """
                SELECT r.rut_residente, r.nombre_residente, r.apellido_residente, v.patente_vehiculo 
                FROM residente r
                LEFT JOIN vehiculo v ON r.rut_residente = v.residente_rut_residente
                WHERE r.no_depto_residente IS NOT NULL
            """
            cursor.execute(query)
            residentes = cursor.fetchall()

            cursor.close()
            conexion.close()
            return residentes
        except Exception as e:
            print(f"Error en la consulta SQL: {e}")
            return []

    # 4. Función para mostrar el reporte de multados entre fechas
    def mostrar_reporte_multados():
        limpiar_tabla()
        configurar_columnas_multados()
        desde = calendario_desde.get_date()
        hasta = calendario_hasta.get_date()

        multados = obtener_multados_fechas(desde, hasta)

        if multados:
            for visita in multados:
                tree.insert("", END, values=(visita[0], visita[1], visita[2], visita[3], visita[4], visita[5]))
        else:
            tree.insert("", END, values=("No hay datos",))

    # 5. Función para mostrar el reporte de residentes (sin filtro de fecha en este caso)
    def mostrar_reporte_residentes():
        limpiar_tabla()
        configurar_columnas_residentes()

        residentes = obtener_residentes_fechas()

        if residentes:
            for residente in residentes:
                tree.insert("", END, values=(residente[0], residente[1], residente[2], residente[3]))
        else:
            tree.insert("", END, values=("No hay datos",))

    # 6. Función para limpiar la tabla antes de mostrar nuevos resultados
    def limpiar_tabla():
        for row in tree.get_children():
            tree.delete(row)

    # 7. Función para configurar columnas específicas para multados
    def configurar_columnas_multados():
        tree["columns"] = ("RUT", "Nombre", "Apellido", "Depto", "Patente", "Ingreso")
        tree.heading("RUT", text="RUT")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Apellido", text="Apellido")
        tree.heading("Depto", text="Depto")
        tree.heading("Patente", text="Patente")
        tree.heading("Ingreso", text="Fecha Ingreso")

        tree.column("RUT", width=100)
        tree.column("Nombre", width=120)
        tree.column("Apellido", width=120)
        tree.column("Depto", width=80)
        tree.column("Patente", width=100)
        tree.column("Ingreso", width=150)

    # 8. Función para configurar columnas específicas para residentes
    def configurar_columnas_residentes():
        tree["columns"] = ("RUT", "Nombre", "Apellido", "Patente")
        tree.heading("RUT", text="RUT")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Apellido", text="Apellido")
        tree.heading("Patente", text="Patente")

        tree.column("RUT", width=100)
        tree.column("Nombre", width=120)
        tree.column("Apellido", width=120)
        tree.column("Patente", width=120)

    # 9. Función para generar el archivo Excel con la tabla de reportes
    def generar_excel():
        # Abre el diálogo para seleccionar la ubicación y el nombre del archivo
        excel_file = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                    filetypes=[("Excel files", "*.xlsx"),
                                                            ("All files", "*.*")])
        if not excel_file:  # Si el usuario cancela, no hacer nada
            return

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Reporte"

        # Títulos de las columnas
        if tipo_reporte.get() == "multados":
            headers = ["RUT", "Nombre", "Apellido", "Depto", "Patente", "Ingreso"]
        else:
            headers = ["RUT", "Nombre", "Apellido", "Patente"]

        sheet.append(headers)

        # Añadir datos a la hoja de cálculo
        for row in tree.get_children():
            values = tree.item(row)["values"]
            sheet.append(values)

        # Guardar el archivo Excel
        workbook.save(excel_file)
        print(f"Excel generado: {excel_file}")

    # 10. Crear la interfaz gráfica con Tkinter
    ventana = Tk()
    ventana.title("Reportes")
    ventana.attributes('-fullscreen', True)  # Hacer que la ventana ocupe toda la pantalla
    ventana.configure(bg='white')  # Fondo blanco

    # Etiqueta de título
    titulo = Label(ventana, text="Reportes", font=("Arial", 16), bg='white')
    titulo.grid(row=0, column=1, pady=10)

    # Opción de selección de tipo de reporte (Multados o Residentes)
    tipo_reporte = StringVar()  # No se le asigna ningún valor predeterminado

    label_opcion = Label(ventana, text="Seleccione una opción:", bg='white')
    label_opcion.grid(row=1, column=0, pady=10)

    radio_multados = Radiobutton(ventana, text="Reportes multados", variable=tipo_reporte, value="multados", bg='white')
    radio_multados.grid(row=1, column=1, pady=10)

    radio_residentes = Radiobutton(ventana, text="Reporte residentes", variable=tipo_reporte, value="residentes", bg='white')
    radio_residentes.grid(row=1, column=2, pady=10)

    # Calendarios de selección de fecha Desde y Hasta
    label_desde = Label(ventana, text="Desde:", bg='white')
    label_desde.grid(row=2, column=1)

    calendario_desde = DateEntry(ventana, width=12, background='darkblue', foreground='white', borderwidth=2)
    calendario_desde.grid(row=2, column=2)

    label_hasta = Label(ventana, text="Hasta:", bg='white')
    label_hasta.grid(row=2, column=3)

    calendario_hasta = DateEntry(ventana, width=12, background='darkblue', foreground='white', borderwidth=2)
    calendario_hasta.grid(row=2, column=4)

    # Botón para mostrar reporte diario de visitas
    boton_diario = Button(ventana, text="Reportes Diarios Visitas", command=lambda: mostrar_reporte_multados() if tipo_reporte.get() == "multados" else mostrar_reporte_residentes(), bg='lightgray')
    boton_diario.grid(row=3, column=0, pady=20)

    # Botón para generar reportes
    boton_generar = Button(ventana, text="Generar Reportes", command=lambda: mostrar_reporte_multados() if tipo_reporte.get() == "multados" else mostrar_reporte_residentes(), bg='lightgray')
    boton_generar.grid(row=3, column=1, pady=20)

    # Botón para limpiar la tabla
    boton_limpiar = Button(ventana, text="Limpiar", command=limpiar_tabla, bg='lightgray')
    boton_limpiar.grid(row=3, column=2, pady=20)

    # Botón para generar Excel
    boton_excel = Button(ventana, text="Generar Excel", command=generar_excel, bg='lightgray')
    boton_excel.grid(row=3, column=3, pady=20)

    # Crear el marco para la tabla de reportes
    frame = ttk.Frame(ventana)
    frame.grid(row=4, column=0, columnspan=5, padx=20, pady=20)

    # Crear el Treeview para mostrar resultados
    tree = ttk.Treeview(frame, show="headings")
    tree.pack(fill="both", expand=True)

    # Crear la barra de desplazamiento vertical
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscroll=scrollbar.set)

    # Iniciar el bucle principal de la interfaz gráfica
    ventana.mainloop()
