import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Crear la ventana principal
root = tk.Tk()
root.title("Autovision - Inicio de Sesión")

# Configurar la ventana en pantalla completa
root.attributes('-fullscreen', True)

# Salir de pantalla completa con la tecla Esc
def salir_pantalla_completa(event):
    root.attributes('-fullscreen', False)

root.bind("<Escape>", salir_pantalla_completa)

# Fondo blanco para la parte superior y negro para la inferior
header_frame = tk.Frame(root, bg='white')
header_frame.pack(fill='both', expand=True)

login_frame = tk.Frame(root, bg='black')
login_frame.pack(fill='both', expand=True)

# Cargar y mostrar el logo de Autovision centrado
image_path = "AUTOVISION.jpg"  # Asegúrate de que esta ruta sea correcta
try:
    logo_img = Image.open(image_path)
    logo_img = logo_img.resize((200, 200), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(header_frame, image=logo_photo, bg='white')
    logo_label.place(relx=0.5, rely=0.3, anchor='center')  # Centrar el logo en la parte superior
except FileNotFoundError:
    print(f"Error: No se pudo abrir la imagen en {image_path}. Verifica la ruta.")

# Texto de "INICIO DE SESIÓN" centrado
inicio_label = tk.Label(header_frame, text="INICIO DE SESIÓN", font=('Arial', 24), bg='white')
inicio_label.place(relx=0.5, rely=0.5, anchor='center')  # Centrar el texto de inicio de sesión

# Etiquetas y campos de texto para el login centrados
usuario_label = tk.Label(login_frame, text="nombre de usuario:", bg='black', fg='white', font=('Arial', 14))
usuario_label.place(relx=0.5, rely=0.1, anchor='center')
usuario_entry = tk.Entry(login_frame, font=('Arial', 14))
usuario_entry.place(relx=0.5, rely=0.2, anchor='center', width=300)

password_label = tk.Label(login_frame, text="Contraseña:", bg='black', fg='white', font=('Arial', 14))
password_label.place(relx=0.5, rely=0.3, anchor='center')
password_entry = tk.Entry(login_frame, font=('Arial', 14), show='*')
password_entry.place(relx=0.5, rely=0.4, anchor='center', width=300)

# "Olvidó su contraseña" centrado
olvide_password_label = tk.Label(login_frame, text="Olvidó su contraseña?", bg='black', fg='white', font=('Arial', 12))
olvide_password_label.place(relx=0.5, rely=0.5, anchor='center')

# Botón de "Iniciar sesión" centrado
login_button = tk.Button(login_frame, text="Iniciar sesión", font=('Arial', 16), bg='yellow', padx=10, pady=5)
login_button.place(relx=0.5, rely=0.6, anchor='center')

# Ejecutar la aplicación
root.mainloop()