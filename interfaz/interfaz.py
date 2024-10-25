import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Necesario para trabajar con imágenes PNG

# Crear la ventana principal
root = tk.Tk()
root.title("Control de Acceso - Visitas")

# Configurar pantalla completa
root.attributes('-fullscreen', True)

# Salir de pantalla completa con la tecla Esc
def salir_pantalla_completa(event):
    root.attributes('-fullscreen', False)

root.bind("<Escape>", salir_pantalla_completa)

# Fondo para el encabezado y el formulario
header_frame = tk.Frame(root, bg='white', height=200)
header_frame.pack(fill='x')

# Botón de "Iniciar Sesión"
iniciar_sesion_button = tk.Button(header_frame, text="Iniciar Sesión", font=('Arial', 16), bg='#87CEEB', padx=10, pady=5)
iniciar_sesion_button.place(x=20, y=20)

# Texto de "Visita"
visita_label = tk.Label(header_frame, text="Visita", font=('Arial', 36), bg='white')
visita_label.place(x=150, y=60)

# Texto de "Patente"
patente_label = tk.Label(header_frame, text="PATENTE", font=('Arial', 18), bg='white')
patente_label.place(x=160, y=140)

# Mostrar la patente detectada
detected_patente = "HZPK49"  # Ejemplo de patente detectada
patente_detectada_label = tk.Label(header_frame, text=detected_patente, font=('Arial', 48, 'bold'), bg='white')
patente_detectada_label.place(x=300, y=120)

# Panel para ingresar datos del visitante
form_frame = tk.Frame(root, bg='#005bac', height=400)
form_frame.pack(fill='both', expand=True)

# Etiquetas y campos de texto para ingresar los datos
nombre_label = tk.Label(form_frame, text="Nombre", bg='#005bac', fg='white', font=('Arial', 14))
nombre_label.place(x=50, y=20)
nombre_entry = tk.Entry(form_frame, font=('Arial', 14))
nombre_entry.place(x=200, y=20, width=400)

apellido_label = tk.Label(form_frame, text="Apellido", bg='#005bac', fg='white', font=('Arial', 14))
apellido_label.place(x=50, y=80)
apellido_entry = tk.Entry(form_frame, font=('Arial', 14))
apellido_entry.place(x=200, y=80, width=400)

rut_label = tk.Label(form_frame, text="RUT", bg='#005bac', fg='white', font=('Arial', 14))
rut_label.place(x=50, y=140)
rut_entry = tk.Entry(form_frame, font=('Arial', 14))
rut_entry.place(x=200, y=140, width=400)

depto_label = tk.Label(form_frame, text="Nro depto", bg='#005bac', fg='white', font=('Arial', 14))
depto_label.place(x=50, y=200)
depto_entry = tk.Entry(form_frame, font=('Arial', 14))
depto_entry.place(x=200, y=200, width=400)

# Botón para guardar la visita
guardar_button = tk.Button(form_frame, text="Guardar Visita", font=('Arial', 16), bg='lightgray', padx=10, pady=5)
guardar_button.place(x=350, y=300)

# Cargar y mostrar la imagen del auto con patente
image_path = "100.png"  # Asegúrate de que la imagen esté en el mismo directorio que el script o ajusta la ruta
try:
    img = Image.open(image_path)
    img = img.resize((400, 200), Image.Resampling.LANCZOS)  # Cambiado de ANTIALIAS a Image.Resampling.LANCZOS
    auto_image = ImageTk.PhotoImage(img)
    auto_image_label = tk.Label(header_frame, image=auto_image, bg='white')
    auto_image_label.place(x=600, y=40)
except FileNotFoundError:
    print(f"Error: No se pudo abrir la imagen en {image_path}. Verifica la ruta.")

# Ejecutar la aplicación
root.mainloop()