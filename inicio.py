import tkinter as tk
from tkinter import font, ttk
from menu import crear_menu
import psycopg2
from bd import conectar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def abrir_ventana_administrador():
    ventana_administrador = tk.Toplevel()
    ventana_administrador.title("Dashboard - Administrador")
    
    # Configuración de la ventana
    ventana_administrador.configure(bg="#212f3d")
    ancho_ventana = ventana_administrador.winfo_screenwidth()
    alto_ventana = ventana_administrador.winfo_screenheight()
    ventana_administrador.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")
    # Crear el menú
    crear_menu(ventana_administrador)
    # Fuente para tarjetas y textos
    card_font = font.Font(family="Arial", size=20, weight="bold")
    title_font = font.Font(family="Arial", size=16, weight="bold")

    # Conectar a la base de datos
    conexion = conectar()
    cursor = conexion.cursor()

    # Consultas de la base de datos
    cursor.execute("SELECT COUNT(*) FROM residente;")
    total_residentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM visita WHERE momento_salida IS NULL;")
    visitas_actuales = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM visita_historico WHERE multado = true;")
    total_multadas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT no_depto_dueno, COUNT(*) as cantidad_visitas 
        FROM visita 
        GROUP BY no_depto_dueno 
        ORDER BY cantidad_visitas DESC 
        LIMIT 5;
    """)
    departamentos, visitas = zip(*cursor.fetchall())

    cursor.execute("""
        SELECT multado, COUNT(*) FROM visita_historico
        GROUP BY multado;
    """)
    multado_data = cursor.fetchall()
    estados = ["True" if row[0] else "False" for row in multado_data]
    porcentajes = [row[1] for row in multado_data]

    # Crear tarjetas de estadísticas
    tarjetas_info = [
        (f"Total Residentes: {total_residentes}", 150),
        (f"Visitas Actuales: {visitas_actuales}", 250),
        (f"Total Visitas Multadas: {total_multadas}", 350),
    ]
    for texto, y in tarjetas_info:
        tk.Label(
            ventana_administrador, text=texto, font=card_font, bg="#34495e", fg="white",
            padx=20, pady=20, width=25, anchor="w"
        ).place(x=30, y=y)

    # Gráfico 1: Departamentos más visitados
    fig1, ax1 = plt.subplots(figsize=(4, 4), dpi=100)
    ax1.pie(visitas, labels=departamentos, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax1.set_title("Departamentos Más Visitados", fontsize=16, color="white")
    fig1.patch.set_facecolor("#212f3d")
    chart1 = FigureCanvasTkAgg(fig1, ventana_administrador)
    chart1.get_tk_widget().place(x=600, y=150)

    # Gráfico 2: Porcentaje de multas
    fig2, ax2 = plt.subplots(figsize=(4, 4), dpi=100)
    ax2.pie(porcentajes, labels=estados, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax2.set_title("Porcentaje de Multas (True/False)", fontsize=12, color="white")
    ax2.tick_params(colors="white") 
    fig2.patch.set_facecolor("#212f3d")
    chart2 = FigureCanvasTkAgg(fig2, ventana_administrador)
    chart2.get_tk_widget().place(x=1000, y=150)
    
    # Título para la tabla
    tk.Label(
        ventana_administrador, text="Top 3 visitantes más frecuentes", font=title_font, bg="#212f3d", fg="white"
    ).place(x=500, y=530)

    # Tabla del Top 3 visitantes más frecuentes
    cursor.execute("""
        SELECT rut_visita_historica, nombre_visita_historica, apellido_visita_historica, COUNT(*) AS total_visitas
        FROM visita_historico
        GROUP BY rut_visita_historica, nombre_visita_historica, apellido_visita_historica
        ORDER BY total_visitas DESC
        LIMIT 3;
    """)
    resultados = cursor.fetchall()
    # Estilo personalizado para la tabla
    estilo_tabla = ttk.Style()
    estilo_tabla.configure(
        "Treeview", 
        font=("Arial", 14),              # Fuente y tamaño para las filas
    )
    estilo_tabla.configure(
        "Treeview.Heading", 
        font=("Arial", 16, "bold"),     # Fuente y tamaño para los encabezados
    )
    estilo_tabla.map(
        "Treeview", 
        background=[("selected", "#2c3e50")],  # Fondo para las filas seleccionadas
        foreground=[("selected", "white")]    # Texto para las filas seleccionadas
    )

    tabla = ttk.Treeview(ventana_administrador, columns=("Rut", "Nombre", "Apellido", "Total Visitas"), show="headings")
    tabla.heading("Rut", text="Rut")
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Apellido", text="Apellido")
    tabla.heading("Total Visitas", text="Total Visitas")
    tabla.column("Rut", anchor="center", width=100)
    tabla.column("Nombre", anchor="center", width=150)
    tabla.column("Apellido", anchor="center", width=150)
    tabla.column("Total Visitas", anchor="center", width=120)

    for fila in resultados:
        tabla.insert("", "end", values=fila)

    tabla.place(x=500, y=580, width=600, height=88)

    # Cerrar conexión
    cursor.close()
    conexion.close()

    # Loop de la aplicación
    ventana_administrador.mainloop()
