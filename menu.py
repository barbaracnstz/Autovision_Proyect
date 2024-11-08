# menú_utils.py
import tkinter as tk
from tkinter import font

def crear_menu(ventana):
    # Crear un Frame en la parte superior para el menú
    menu_frame = tk.Frame(ventana, bg="#4db6ac")
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
        
    def go_to_administradores():
        ventana.destroy()
        from administradores import abrir_ventana_administradores
        abrir_ventana_administradores()

    def go_to_mi_perfil():
        ventana.destroy()
        from perfil import abrir_ventana_mi_perfil
        abrir_ventana_mi_perfil()
        
    def cerrar_sesion():
        ventana.destroy()
        from inicio_sesion import abrir_ventana_inicio
        abrir_ventana_inicio()

    # Crear los botones del menú con estilo
    btn_inicio = tk.Button(menu_frame, text="🏠 Inicio", command=go_to_inicio, font=button_font,
                           bg="#4db6ac", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_inicio.pack(side=tk.LEFT, padx=10)

    btn_residentes = tk.Button(menu_frame, text="👥 Residentes", command=go_to_residentes, font=button_font,
                               bg="#4db6ac", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_residentes.pack(side=tk.LEFT, padx=10)

    btn_reportes = tk.Button(menu_frame, text="📊 Reportes", command=go_to_reportes, font=button_font,
                             bg="#4db6ac", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_reportes.pack(side=tk.LEFT, padx=10)

    btn_administradores = tk.Button(menu_frame, text="🛠️ Administradores", command=go_to_administradores, font=button_font,
                                    bg="#4db6ac", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_administradores.pack(side=tk.LEFT, padx=10)

    btn_mi_perfil = tk.Button(menu_frame, text="👤 Mi Perfil", command=go_to_mi_perfil, font=button_font,
                              bg="#4db6ac", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_mi_perfil.pack(side=tk.LEFT, padx=10)
    
    btn_cerrar_sesion = tk.Button(menu_frame, text="Cerrar Sesión", command=cerrar_sesion, font=button_font,
                              bg="#4db6ac", fg="white", bd=0, activebackground="white", activeforeground="black", padx=15)
    btn_cerrar_sesion.pack(side=tk.RIGHT, padx=10)
