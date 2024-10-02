import tkinter as tk
from PIL import Image, ImageTk

# Función para mostrar el logo
def mostrar_logo():
    # Crear la ventana
    ventana = tk.Tk()
    ventana.title("Sistema Autovisión")
    
    # Cargar la imagen
    imagen = Image.open("AUTOVISION.jpg")
    imagen_logo = ImageTk.PhotoImage(imagen)

    # Crear un Label para mostrar la imagen
    label_logo = tk.Label(ventana, image=imagen_logo)
    
    # Posicionar el logo en la esquina superior derecha
    label_logo.place(x=ventana.winfo_screenwidth()-imagen.width(), y=0)
    
    # Iniciar el loop de la ventana
    ventana.mainloop()

# Llamar a la función para mostrar la ventana
mostrar_logo()
