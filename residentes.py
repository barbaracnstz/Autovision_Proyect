import tkinter as tk

def abrir_ventana_residentes():
    # Crear la nueva ventana de residentes
    ventana_residentes = tk.Toplevel()
    ventana_residentes.title("Vista de Residentes")

    # Obtener el tamaño de la pantalla
    ancho_ventana = ventana_residentes.winfo_screenwidth()
    alto_ventana = ventana_residentes.winfo_screenheight()

    # Ajustar la ventana al tamaño de la pantalla
    ventana_residentes.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")

    etiqueta = tk.Label(ventana_residentes, text="Bienvenido a la Vista de Residentes")
    etiqueta.pack()

    # Agrega más widgets a la ventana de residentes según sea necesario
    # ...
