import tkinter as tk
from tkinter import font
import psycopg2
from bd import conectar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from menu import crear_menu


def abrir_ventana_administrador():
    ventana_administrador = tk.Toplevel()
    ventana_administrador.title("Dashboard - Administrador")    
    
    # Obtener el tamaño de la pantalla y ajustar la ventana
    ancho_ventana = ventana_administrador.winfo_screenwidth()
    alto_ventana = ventana_administrador.winfo_screenheight()
    ventana_administrador.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")
    
    #Menu
    crear_menu(ventana_administrador)
    
    # Fuente para las tarjetas
    card_font = font.Font(family="Arial", size=16, weight="bold")

    # Conectar a la base de datos
    conexion = conectar()
    cursor = conexion.cursor()

    # Obtener el total de residentes
    cursor.execute("SELECT COUNT(*) FROM residente;")
    total_residentes = cursor.fetchone()[0]

    # Obtener la cantidad de visitas actuales
    cursor.execute("SELECT COUNT(*) FROM visita WHERE momento_salida IS NULL;")
    visitas_actuales = cursor.fetchone()[0]

    # Crear tarjetas de estadísticas
    lbl_residentes = tk.Label(ventana_administrador, text=f"Total Residentes: {total_residentes}", font=card_font, bg="#4db6ac", fg="white", padx=20, pady=10)
    lbl_residentes.pack(pady=10)
    lbl_visitas = tk.Label(ventana_administrador, text=f"Visitas Actuales: {visitas_actuales}", font=card_font, bg="#4db6ac", fg="white", padx=20, pady=10)
    lbl_visitas.pack(pady=10)

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
