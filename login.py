import tkinter as tk
from tkinter import messagebox
from util import validar_login  # Desde util.py llamamos la funcion 
from residentes import abrir_ventana_residentes  # Importa la función que abre la nueva ventana

# Crear la ventana de inicio de sesión
ventana_login = tk.Tk()
ventana_login.title("Inicio de Sesión")

# Obtener el tamaño de la pantalla
ancho_ventana = ventana_login.winfo_screenwidth()
alto_ventana = ventana_login.winfo_screenheight()

# Ajustar la ventana al tamaño de la pantalla
ventana_login.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")

# Widgets de la ventana de login
etiqueta_usuario = tk.Label(ventana_login, text="Usuario:")
etiqueta_usuario.pack()

entrada_usuario = tk.Entry(ventana_login)
entrada_usuario.pack()

etiqueta_contrasena = tk.Label(ventana_login, text="Contraseña:")
etiqueta_contrasena.pack()

entrada_contrasena = tk.Entry(ventana_login, show="*")
entrada_contrasena.pack()

def iniciar_sesion():
    usuario = entrada_usuario.get()
    contrasena = entrada_contrasena.get()

    # Validar los datos de login
    if validar_login(usuario, contrasena):
        messagebox.showinfo("Éxito", "Inicio de sesión correcto")
        # Ocultar la ventana de login
        ventana_login.withdraw()

        # Abrir la ventana de residentes
        abrir_ventana_residentes()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

# Botón para iniciar sesión
boton_iniciar = tk.Button(ventana_login, text="Iniciar sesión", command=iniciar_sesion)
boton_iniciar.pack()

# Ejecutar la ventana
# despues de ejecutar tira error el proyecto tiene que tener solo uno y ya hay uno, al juntar todo eliminar este comando
ventana_login.mainloop()