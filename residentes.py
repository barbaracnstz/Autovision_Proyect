import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Para el logo
from bd import obtener_residentes, editar_residente, eliminar_residente, agregar_residente

def abrir_ventana_residentes():
    ventana_residentes = tk.Toplevel()
    ventana_residentes.title("Vista de Residentes")

    # Obtener el tamaño de la pantalla y ajustar la ventana
    ancho_ventana = ventana_residentes.winfo_screenwidth()
    alto_ventana = ventana_residentes.winfo_screenheight()
    ventana_residentes.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")

    # Estilos para botones y widgets
    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.configure('TLabel', font=('Helvetica', 12))

    # Cargar logo
    # imagen_logo = Image.open("logo.png")  # Asegúrate de tener un archivo llamado logo.png
    # imagen_logo = imagen_logo.resize((100, 100), Image.ANTIALIAS)
    # logo = ImageTk.PhotoImage(imagen_logo)

    # label_logo = tk.Label(ventana_residentes, image=logo)
    # label_logo.image = logo  # Mantener referencia para evitar que se elimine
    # label_logo.grid(row=0, column=0, padx=20, pady=20)

    # Tabla con los residentes
    columnas = ('rut', 'nombre_apellido', 'telefono', 'nro_depto', 'patente')
    tabla_residentes = ttk.Treeview(ventana_residentes, columns=columnas, show='headings', height=20)
    tabla_residentes.heading('rut', text='RUT')
    tabla_residentes.heading('nombre_apellido', text='Nombre y Apellido')
    tabla_residentes.heading('telefono', text='Teléfono')
    tabla_residentes.heading('nro_depto', text='Nro. Depto')
    tabla_residentes.heading('patente', text='Patente Vehículo')
    tabla_residentes.grid(row=1, column=0, columnspan=4, padx=20, pady=10)

    # Función para cargar los residentes en la tabla
    def cargar_residentes():
        for i in tabla_residentes.get_children():
            tabla_residentes.delete(i)

        residentes = obtener_residentes()
        for residente in residentes:
            rut_completo = f"{residente['rut_residente']}-{residente['dv_residente']}"
            nombre_completo = f"{residente['nombre_residente']} {residente['apellido_residente']}"
            tabla_residentes.insert("", tk.END, values=(rut_completo, nombre_completo, residente['telefono_residente'], residente['no_depto_residente'], residente['patente_vehiculo']))

    # Llamar a la función para cargar residentes
    cargar_residentes()

    # Ventana emergente para editar residente
    def abrir_ventana_editar(residente):
        ventana_editar = tk.Toplevel(ventana_residentes)
        ventana_editar.title("Editar Residente")
        ventana_editar.geometry("400x300")

        rut, nombre_apellido, telefono, nro_depto, patente = residente

        ttk.Label(ventana_editar, text="Teléfono:").pack()
        entrada_telefono = ttk.Entry(ventana_editar)
        entrada_telefono.insert(0, telefono)
        entrada_telefono.pack()

        ttk.Label(ventana_editar, text="Nro. Depto:").pack()
        entrada_nro_depto = ttk.Entry(ventana_editar)
        entrada_nro_depto.insert(0, nro_depto)
        entrada_nro_depto.pack()

        ttk.Label(ventana_editar, text="Patente:").pack()
        entrada_patente = ttk.Entry(ventana_editar)
        entrada_patente.insert(0, patente)
        entrada_patente.pack()

        def guardar_cambios():
            nuevo_telefono = entrada_telefono.get()
            nuevo_nro_depto = entrada_nro_depto.get()
            nueva_patente = entrada_patente.get()
            rut_residente = rut.split("-")[0]

            editar_residente(rut_residente, nuevo_telefono, nuevo_nro_depto, nueva_patente)
            messagebox.showinfo("Éxito", "Residente editado correctamente")
            ventana_editar.destroy()
            cargar_residentes()

        ttk.Button(ventana_editar, text="Guardar Cambios", command=guardar_cambios).pack(pady=5)
        ttk.Button(ventana_editar, text="Cancelar", command=ventana_editar.destroy).pack(pady=5)

    # Funciones para los botones de editar, eliminar y agregar
    def editar_residente_callback():
        item_seleccionado = tabla_residentes.selection()
        if item_seleccionado:
            residente_seleccionado = tabla_residentes.item(item_seleccionado)['values']
            abrir_ventana_editar(residente_seleccionado)
        else:
            messagebox.showerror("Error", "Seleccione un residente para editar")

    def eliminar_residente_callback():
        item_seleccionado = tabla_residentes.selection()
        if item_seleccionado:
            residente_seleccionado = tabla_residentes.item(item_seleccionado)['values']
            if messagebox.askyesno("Eliminar", f"¿Está seguro de eliminar a {residente_seleccionado[1]}?"):
                rut_residente = residente_seleccionado[0].split("-")[0]
                eliminar_residente(rut_residente)
                cargar_residentes()
        else:
            messagebox.showerror("Error", "Seleccione un residente para eliminar")

    def abrir_ventana_agregar():
        ventana_agregar = tk.Toplevel(ventana_residentes)
        ventana_agregar.title("Agregar Residente")
        ventana_agregar.geometry("400x400")

        campos = ['RUT', 'DV', 'Nombre', 'Apellido', 'Fecha Nacimiento', 'Teléfono', 'Nro. Depto', 'Patente Vehículo']
        entradas = {}
        for campo in campos:
            ttk.Label(ventana_agregar, text=f"{campo}:").pack(pady=5)
            entrada = ttk.Entry(ventana_agregar)
            entrada.pack(pady=5)
            entradas[campo] = entrada

        def guardar_nuevo_residente():
            rut = entradas['RUT'].get()
            dv = entradas['DV'].get()
            nombre = entradas['Nombre'].get()
            apellido = entradas['Apellido'].get()
            fecha = entradas['Fecha Nacimiento'].get()
            telefono = entradas['Teléfono'].get()
            nro_depto = entradas['Nro. Depto'].get()
            patente = entradas['Patente Vehículo'].get()

            agregar_residente(rut, dv, nombre, apellido, fecha, telefono, nro_depto, patente)
            messagebox.showinfo("Éxito", "Residente agregado correctamente")
            ventana_agregar.destroy()
            cargar_residentes()

        ttk.Button(ventana_agregar, text="Guardar", command=guardar_nuevo_residente).pack(pady=10)
        ttk.Button(ventana_agregar, text="Cancelar", command=ventana_agregar.destroy).pack(pady=10)

    # Barra de búsqueda
    def buscar_residente():
        criterio = entrada_busqueda.get().lower()
        for item in tabla_residentes.get_children():
            residente = tabla_residentes.item(item)['values']
            nombre_completo = residente[1].lower()
            nro_depto = str(residente[3])
            if criterio in nombre_completo or criterio in nro_depto:
                tabla_residentes.selection_set(item)
                break

    ttk.Label(ventana_residentes, text="Buscar:").grid(row=0, column=1, padx=10, pady=10)
    entrada_busqueda = ttk.Entry(ventana_residentes, width=30)
    entrada_busqueda.grid(row=0, column=2, padx=10, pady=10)
    ttk.Button(ventana_residentes, text="Buscar", command=buscar_residente).grid(row=0, column=3, padx=10, pady=10)

    # Botones de acción
    ttk.Button(ventana_residentes, text="Editar", command=editar_residente_callback).grid(row=2, column=0, padx=10, pady=10)
    ttk.Button(ventana_residentes, text="Eliminar", command=eliminar_residente_callback).grid(row=2, column=1, padx=10, pady=10)
    ttk.Button(ventana_residentes, text="Agregar Residente", command=abrir_ventana_agregar).grid(row=2, column=2, padx=10, pady=10)

    # Función para cerrar sesión
    def cerrar_sesion():
        ventana_residentes.destroy()
        import inicio_sesion  # Dirige a la página de inicio de sesión

    # Botón de cerrar sesión
    ttk.Button(ventana_residentes, text="Cerrar Sesión", command=cerrar_sesion).grid(row=2, column=3, padx=10, pady=10)
