import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from util import validar_login  # Importa la función para validar el login
from residentes import abrir_ventana_residentes  # Importa la función para abrir la ventana de residentes

# Crear la ventana principal
root = tk.Tk()
root.title("Autovision - Inicio de Sesión")


# Obtener el tamaño de la pantalla
ancho_ventana = root.winfo_screenwidth()
alto_ventana = root.winfo_screenheight()

# Ajustar la ventana al tamaño de la pantalla
root.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")

# Salir de pantalla completa con la tecla Esc
def salir_pantalla_completa(event):
    root.attributes('-fullscreen', False)

root.bind("<Escape>", salir_pantalla_completa)

# Marco superior (encabezado)
header_frame = tk.Frame(root, bg='white')
header_frame.pack(fill='both', expand=True)

# Marco inferior (login)
login_frame = tk.Frame(root, bg='black')
login_frame.pack(fill='both', expand=True)

# Texto de "INICIO DE SESIÓN" centrado
inicio_label = tk.Label(header_frame, text="INICIO DE SESIÓN", font=('Arial', 24), bg='white')
inicio_label.place(relx=0.5, rely=0.5, anchor='center')  # Centrar el texto de inicio de sesión

# Etiquetas y campos de texto para el login centrados
usuario_label = tk.Label(login_frame, text="RUT sin dígito verificador:", bg='black', fg='white', font=('Arial', 14))
usuario_label.place(relx=0.5, rely=0.1, anchor='center')
usuario_entry = tk.Entry(login_frame, font=('Arial', 14))
usuario_entry.place(relx=0.5, rely=0.2, anchor='center', width=300)

password_label = tk.Label(login_frame, text="Contraseña:", bg='black', fg='white', font=('Arial', 14))
password_label.place(relx=0.5, rely=0.3, anchor='center')
password_entry = tk.Entry(login_frame, font=('Arial', 14), show='*')
password_entry.place(relx=0.5, rely=0.4, anchor='center', width=300)

# "Olvidó su contraseña" centrado
olvide_password_label = tk.Label(login_frame, text="¿Olvidó su contraseña?", bg='black', fg='white', font=('Arial', 12))
olvide_password_label.place(relx=0.5, rely=0.5, anchor='center')

# Función para iniciar sesión
def iniciar_sesion():
    usuario = usuario_entry.get()
    contrasena = password_entry.get()

    # Validar los datos de login
    if validar_login(usuario, contrasena):
        messagebox.showinfo("Éxito", "Inicio de sesión correcto")
        # Ocultar la ventana de inicio de sesión
        root.withdraw()

        # Abrir la ventana de residentes
        abrir_ventana_residentes()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

# Botón de "Iniciar sesión" centrado
login_button = tk.Button(login_frame, text="Iniciar sesión", font=('Arial', 16), bg='yellow', padx=10, pady=5, command=iniciar_sesion)
login_button.place(relx=0.5, rely=0.6, anchor='center')

# Ejecutar la aplicación
root.mainloop()
