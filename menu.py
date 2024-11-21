# menú_utils.py
import tkinter as tk
from tkinter import font

def crear_menu(ventana):
    # Crear un Frame en la parte superior para el menú
    menu_frame = tk.Frame(ventana, bg="#212f3d")
    menu_frame.pack(fill=tk.X)  # Sin pady

    # Crear estilo de fuente para los botones
    button_font = font.Font(family="Arial", size=15, weight="bold")

    # Funciones para abrir ventanas
    def go_to_inicio():
        ventana.destroy()
        from inicio import abrir_ventana_administrador
        abrir_ventana_administrador()

    def go_to_residentes():
        ventana.destroy()
        from residentes import abrir_ventana_residentes 
        abrir_ventana_residentes()

    def go_to_reportes():
        ventana.destroy()
        from reportes import abrir_ventana_reportes
        abrir_ventana_reportes()
        
    def cerrar_sesion():
        ventana.destroy()
        from inicio_sesion import abrir_ventana_inicio
        abrir_ventana_inicio()

    # Crear los botones del menú con estilo
    btn_inicio = tk.Button(menu_frame, text="🏠 Inicio", command=go_to_inicio, font=button_font,
                           bg="#212f3d", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_inicio.pack(side=tk.LEFT, padx=10)

    btn_residentes = tk.Button(menu_frame, text="👥 Residentes", command=go_to_residentes, font=button_font,
                               bg="#212f3d", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_residentes.pack(side=tk.LEFT, padx=10)

    btn_reportes = tk.Button(menu_frame, text="📊 Reportes", command=go_to_reportes, font=button_font,
                             bg="#212f3d", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_reportes.pack(side=tk.LEFT, padx=10)
    
    btn_cerrar_sesion = tk.Button(menu_frame, text="Cerrar Sesión", command=cerrar_sesion, font=button_font,
                              bg="#212f3d", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_cerrar_sesion.pack(side=tk.RIGHT, padx=10)
