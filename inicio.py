import tkinter as tk
from tkinter import font
import psycopg2
from bd import conectar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from menu import crear_menu
from tkinter import ttk


def abrir_ventana_administrador():
    ventana_administrador = tk.Toplevel()
    ventana_administrador.title("Dashboard - Administrador")    
    
    # Obtener el tamaño de la pantalla y ajustar la ventana
    ancho_ventana = ventana_administrador.winfo_screenwidth()
    alto_ventana = ventana_administrador.winfo_screenheight()
    ventana_administrador.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")
    
    # Fuente para las tarjetas
    card_font = font.Font(family="Arial", size=16, weight="bold")
    
    # Cargar la imagen de fondo
    fondo_img = Image.open("fondoform.png")
    fondo_img = fondo_img.resize((1670, 800), Image.LANCZOS)  # Cambiar a LANCZOS
    fondo_photo = ImageTk.PhotoImage(fondo_img)

    # Crear un label para la imagen de fondo
    label_fondo = tk.Label(ventana_administrador, image=fondo_photo)
    label_fondo.place(relwidth=1, relheight=1)  # Ajustar a todo el fondo

    # Menu
    crear_menu(ventana_administrador)
    
    # Conectar a la base de datos
    conexion = conectar()
    cursor = conexion.cursor()

    # Obtener el total de residentes
    cursor.execute("SELECT COUNT(*) FROM residente;")
    total_residentes = cursor.fetchone()[0]

    # Obtener el total de vehiculos
    cursor.execute("SELECT COUNT(*) FROM vehiculo;")
    total_vehiculo = cursor.fetchone()[0]

    # Obtener la cantidad de visitas actuales
    cursor.execute("SELECT COUNT(*) FROM visita WHERE momento_salida IS NULL;")
    visitas_actuales = cursor.fetchone()[0]

    # Consulta SQL para contar las visitas multadas
    cursor.execute("SELECT COUNT(*) FROM visita_historico WHERE multado = true")
    total_multadas = cursor.fetchone()[0]   
    
    # Consulta SQL para obtener el top 3 de visitantes más frecuentes
    cursor.execute("""
            SELECT rut_visita_historica, nombre_visita_historica, apellido_visita_historica, COUNT(*) AS total_visitas
            FROM visita_historico
            GROUP BY rut_visita_historica, nombre_visita_historica, apellido_visita_historica
            ORDER BY total_visitas DESC
            LIMIT 3
    """)
    resultados = cursor.fetchall()  # Obtener todos los resultados

    # Crear tarjetas de estadísticas
    lbl_residentes = tk.Label(ventana_administrador, text=f"Total Residentes: {total_residentes}", font=card_font, bg="#4db6ac", fg="white", padx=20, pady=10)
    lbl_residentes.pack(pady=10)

    lbl_visitas_actuales = tk.Label(ventana_administrador, text=f"Visitas Actuales: {visitas_actuales}", font=card_font, bg="#4db6ac", fg="white", padx=20, pady=10)
    lbl_visitas_actuales.pack(pady=10)

    lbl_vehiculos = tk.Label(ventana_administrador, text=f"Total vehiculos: {total_vehiculo}", font=card_font, bg="#4db6ac", fg="white", padx=20, pady=10)
    lbl_vehiculos.pack(pady=10)

    lbl_multadas = tk.Label(ventana_administrador, text=f"Total visitas multadas: {total_multadas}", font=card_font, bg="#4db6ac", fg="white", padx=20, pady=10)
    lbl_multadas.pack(pady=10)

    # Título de la ventana para el Top 3 de visitantes
    titulo_label = tk.Label(ventana_administrador, text="Top 3 Visitantes Más Frecuentes", font=("Arial", 14), bg="#4db6ac", fg="white")
    titulo_label.place(x=200, y=60)  # Posiciona el título en (400, 10)

    # Crear la tabla para mostrar los resultados del top 3
    tabla = ttk.Treeview(ventana_administrador, columns=("Rut", "Nombre", "Apellido", "Total Visitas"), show="headings")
    tabla.heading("Rut", text="Rut")
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Apellido", text="Apellido")
    tabla.heading("Total Visitas", text="Total Visitas")

    # Configurar el tamaño de las columnas
    tabla.column("Rut", width=100, anchor="center")
    tabla.column("Nombre", width=150, anchor="center")
    tabla.column("Apellido", width=150, anchor="center")
    tabla.column("Total Visitas", width=120, anchor="center")

    # Ejemplo de datos
    resultados = [("12345678-9", "Juan", "Pérez", 10),
                ("98765432-1", "Ana", "López", 8),
                ("11223344-5", "Carlos", "Gómez", 6)]

    # Insertar los datos en la tabla
    for visitante in resultados:
        tabla.insert("", "end", values=visitante)

    # Posicionar la tabla en una posición manual
    tabla.place(x=60, y=100, width=500, height=200)
    # Obtener datos para el gráfico
    cursor.execute("""
        SELECT no_depto_dueno, COUNT(*) as cantidad_visitas 
        FROM visita 
        GROUP BY no_depto_dueno 
        ORDER BY cantidad_visitas DESC 
        LIMIT 5;
    """)
    departamentos, visitas = zip(*cursor.fetchall())

    # Crear el gráfico de barras
    fig, ax = plt.subplots()
    ax.bar(departamentos, visitas, color="#4db6ac")
    ax.set_xlabel("Número de Departamento")
    ax.set_ylabel("Cantidad de Visitas")
    ax.set_title("Departamentos con Más Visitas")

    # Mostrar el gráfico en tkinter
    chart = FigureCanvasTkAgg(fig, ventana_administrador)
    chart.get_tk_widget().pack(pady=20)

    # Cerrar conexión
    cursor.close()
    conexion.close()

    # Iniciar el loop de la aplicación
    ventana_administrador.mainloop()
