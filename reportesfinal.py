import psycopg2
from tkinter import Tk, Label, Button, Radiobutton, StringVar, END
from tkcalendar import DateEntry
from tkinter import ttk
from datetime import datetime

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
            WHERE momento_ingreso_historico >= %s AND momento_ingreso_historico <= %s
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

# 3. Función para obtener residentes entre fechas
def obtener_residentes_fechas(desde, hasta):
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

# 5. Función para mostrar el reporte de residentes entre fechas
def mostrar_reporte_residentes():
    limpiar_tabla()
    configurar_columnas_residentes()
    desde = calendario_desde.get_date()
    hasta = calendario_hasta.get_date()

    residentes = obtener_residentes_fechas(desde, hasta)

    if residentes:
        for residente in residentes:
            tree.insert("", END, values=(residente[0], residente[1], residente[2], residente[3]))
    else:
        tree.insert("", END, values=("No hay datos",))

# 6. Función para mostrar el reporte diario de visitas
def mostrar_reporte_diario():
    limpiar_tabla()
    configurar_columnas_multados()  # El reporte diario muestra columnas de multados
    hoy = datetime.now().date()

    visitas = obtener_multados_fechas(hoy, hoy)

    if visitas:
        for visita in visitas:
            tree.insert("", END, values=(visita[0], visita[1], visita[2], visita[3], visita[4], visita[5]))
    else:
        tree.insert("", END, values=("No hay visitas registradas hoy."))

# 7. Función para limpiar la tabla antes de mostrar nuevos resultados
def limpiar_tabla():
    for row in tree.get_children():
        tree.delete(row)

# 8. Función para configurar columnas específicas para multados
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

# 9. Función para configurar columnas específicas para residentes
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

# 10. Crear la interfaz gráfica con Tkinter
ventana = Tk()
ventana.title("Reportes")
ventana.geometry("800x600")

# Etiqueta de título
titulo = Label(ventana, text="Reportes", font=("Arial", 16))
titulo.grid(row=0, column=1, pady=10)

# Opción de selección de tipo de reporte (Multados o Residentes)
tipo_reporte = StringVar()  # No se le asigna ningún valor predeterminado

label_opcion = Label(ventana, text="Seleccione una opción:")
label_opcion.grid(row=1, column=0, pady=10)

radio_multados = Radiobutton(ventana, text="Reportes multados", variable=tipo_reporte, value="multados")
radio_multados.grid(row=1, column=1, pady=10)

radio_residentes = Radiobutton(ventana, text="Reporte residentes", variable=tipo_reporte, value="residentes")
radio_residentes.grid(row=1, column=2, pady=10)

# Calendarios de selección de fecha Desde y Hasta
label_desde = Label(ventana, text="Desde:")
label_desde.grid(row=2, column=0)

calendario_desde = DateEntry(ventana, width=12, background='darkblue', foreground='white', borderwidth=2)
calendario_desde.grid(row=2, column=1)

label_hasta = Label(ventana, text="Hasta:")
label_hasta.grid(row=2, column=2)

calendario_hasta = DateEntry(ventana, width=12, background='darkblue', foreground='white', borderwidth=2)
calendario_hasta.grid(row=2, column=3)

# Botón para generar el reporte diario de visitas
boton_diario = Button(ventana, text="Reporte Diarios Visitas", command=mostrar_reporte_diario)
boton_diario.grid(row=3, column=0, pady=20)

# Botón para generar reportes según selección (Multados o Residentes)
def generar_reporte():
    if tipo_reporte.get() == "multados":
        mostrar_reporte_multados()
    elif tipo_reporte.get() == "residentes":
        mostrar_reporte_residentes()
    else:
        limpiar_tabla()
        tree.insert("", END, values=("Por favor, seleccione una opción de reporte.",))

boton_generar = Button(ventana, text="Generar Reportes", command=generar_reporte)
boton_generar.grid(row=3, column=3, pady=20)

# Creación de la tabla con Treeview
tree = ttk.Treeview(ventana, columns=(), show="headings")
tree.grid(row=4, column=0, columnspan=4, padx=20, pady=20)

# Ejecutar la interfaz gráfica
ventana.mainloop()
