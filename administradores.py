import tkinter as tk
from tkinter import messagebox
from bd import conectar, cargar_datos_admins
from menu import crear_menu


def abrir_ventana_administradores():
    ventana_administradores = tk.Toplevel()
    ventana_administradores.title("Administradores")
    
    # Crear el menú
    crear_menu(ventana_administradores)

    # Obtener el tamaño de la pantalla y ajustar la ventana
    ancho_ventana = ventana_administradores.winfo_screenwidth()
    alto_ventana = ventana_administradores.winfo_screenheight()
    ventana_administradores.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")

    # Crear un Frame para los controles (barra de búsqueda y paginación)
    frame_controles = tk.Frame(ventana_administradores)
    frame_controles.pack(pady=20)

    label_titulo = tk.Label(frame_controles, text="Lista de Administradores", font=("Arial", 14, "bold"))
    label_titulo.grid(row=0, column=0, columnspan=2, pady=10)

    # Barra de búsqueda
    tk.Label(frame_controles, text="Buscar:").grid(row=1, column=0, padx=10)
    entry_buscar = tk.Entry(frame_controles, width=30)
    entry_buscar.grid(row=1, column=1, padx=10)

    # Función para actualizar el texto de búsqueda y recargar la tabla
    def actualizar_busqueda(event=None):
        nonlocal texto_busqueda
        texto_busqueda = entry_buscar.get().lower()
        cargar_datos_tabla()  # Recargar la tabla con el filtro aplicado

    # Asociar la tecla de búsqueda con la función para actualizar
    entry_buscar.bind("<KeyRelease>", actualizar_busqueda)

    # Crear un botón para agregar un administrador
    def abrir_modal_agregar_admin():
        modal = tk.Toplevel()
        modal.title("Agregar Administrador")

        # Crear formulario para ingresar los datos
        label_rut = tk.Label(modal, text="RUT Administrador")
        label_rut.grid(row=0, column=0, padx=10, pady=10)
        entry_rut = tk.Entry(modal)
        entry_rut.grid(row=0, column=1, padx=10)

        label_nombre = tk.Label(modal, text="Nombre")
        label_nombre.grid(row=1, column=0, padx=10)
        entry_nombre = tk.Entry(modal)
        entry_nombre.grid(row=1, column=1, padx=10)

        label_apellido = tk.Label(modal, text="Apellido")
        label_apellido.grid(row=2, column=0, padx=10)
        entry_apellido = tk.Entry(modal)
        entry_apellido.grid(row=2, column=1, padx=10)

        label_telefono = tk.Label(modal, text="Teléfono")
        label_telefono.grid(row=3, column=0, padx=10)
        entry_telefono = tk.Entry(modal)
        entry_telefono.grid(row=3, column=1, padx=10)

        label_correo = tk.Label(modal, text="Correo")
        label_correo.grid(row=4, column=0, padx=10)
        entry_correo = tk.Entry(modal)
        entry_correo.grid(row=4, column=1, padx=10)

        label_cargo = tk.Label(modal, text="Cargo")
        label_cargo.grid(row=5, column=0, padx=10)
        entry_cargo = tk.Entry(modal)
        entry_cargo.grid(row=5, column=1, padx=10)

        label_estado = tk.Label(modal, text="Estado (True/False)")
        label_estado.grid(row=6, column=0, padx=10)
        entry_estado = tk.Entry(modal)
        entry_estado.grid(row=6, column=1, padx=10)

        # Función para guardar el nuevo administrador
        def guardar_admin():
            rut = entry_rut.get()
            nombre = entry_nombre.get()
            apellido = entry_apellido.get()
            telefono = entry_telefono.get()
            correo = entry_correo.get()
            cargo = entry_cargo.get()
            estado = entry_estado.get().lower() == 'true'  # Convertir a booleano (True o False)

            if not rut or not nombre or not telefono or not cargo:
                messagebox.showwarning("Campos incompletos", "Por favor, complete todos los campos obligatorios.")
                return

            # Guardar en la base de datos (ejemplo de función de inserción)
            insertar_admin(rut, nombre, apellido, telefono, correo, cargo, estado)
            messagebox.showinfo("Éxito", "Administrador agregado correctamente.")
            modal.destroy()
            cargar_datos_tabla()  # Recargar la tabla para mostrar el nuevo administrador

        # Botón para guardar
        btn_guardar = tk.Button(modal, text="Guardar", command=guardar_admin)
        btn_guardar.grid(row=7, column=0, columnspan=2, pady=10)

    # Crear botón "Agregar Administrador"
    btn_agregar_admin = tk.Button(ventana_administradores, text="Agregar Administrador", command=abrir_modal_agregar_admin)
    btn_agregar_admin.pack(pady=20)

    # Variables para manejar la paginación y búsqueda
    registros_por_pagina = 10
    pagina_actual = 0
    texto_busqueda = ""

    # Función para cargar los datos en la tabla con paginación y búsqueda
    def cargar_datos_tabla():
        # Limpiar la tabla antes de cargar nuevos datos
        for widget in frame_tabla.winfo_children():
            widget.grid_forget()

        # Encabezados de la tabla
        encabezados = ["RUT", "Nombre", "Apellido", "Teléfono", "Correo", "Cargo", "Estado", "Acción"]
        for i, encabezado in enumerate(encabezados):
            label = tk.Label(frame_tabla, text=encabezado, font=('Arial', 10, 'bold'), borderwidth=1, relief="solid", width=15)
            label.grid(row=0, column=i, sticky="nsew")

        # Obtener los datos de la base de datos
        admins = cargar_datos_admins()

        # Filtrar los registros si hay texto de búsqueda
        if texto_busqueda:
            admins = [r for r in admins if any(texto_busqueda in str(dato).lower() for dato in r)]

        # Calcular los registros a mostrar para la página actual
        inicio = pagina_actual * registros_por_pagina
        fin = inicio + registros_por_pagina
        admins_pagina = admins[inicio:fin]

        # Añadir datos a la tabla
        for row_num, admin in enumerate(admins_pagina, start=1):
            for col_num, dato in enumerate(admin):
                label = tk.Label(frame_tabla, text=dato, borderwidth=1, relief="solid", width=15)
                label.grid(row=row_num, column=col_num, sticky="nsew")

            # Variable para el estado seleccionado
            estado_seleccionado = tk.StringVar(value=admin[6])  # Estado actual

            # Crear el OptionMenu para cambiar el estado
            menu_estado = tk.OptionMenu(frame_tabla, estado_seleccionado, "Activo", "Inactivo")
            menu_estado.grid(row=row_num, column=6, sticky="nsew")

            # Botón EDITAR
            btn_editar = tk.Button(frame_tabla, text="EDITAR", bg="yellow", command=lambda rut=admin[0]: editar_admin(rut))
            btn_editar.grid(row=row_num, column=7, sticky="nsew")


        # Actualizar los botones de paginación
        actualizar_botones_paginacion(len(admins))

    # Función para actualizar los botones de paginación
    def actualizar_botones_paginacion(total_registros):
        if pagina_actual > 0:
            btn_anterior.config(state="normal")
        else:
            btn_anterior.config(state="disabled")

        if (pagina_actual + 1) * registros_por_pagina < total_registros:
            btn_siguiente.config(state="normal")
        else:
            btn_siguiente.config(state="disabled")

    # Crear la tabla de datos
    frame_tabla = tk.Frame(ventana_administradores)
    frame_tabla.pack(pady=20)

    # Crear los botones de paginación
    frame_paginacion = tk.Frame(ventana_administradores)
    frame_paginacion.pack(pady=20)

    btn_anterior = tk.Button(frame_paginacion, text="Anterior", command=lambda: cambiar_pagina(-1))
    btn_anterior.grid(row=0, column=0)

    btn_siguiente = tk.Button(frame_paginacion, text="Siguiente", command=lambda: cambiar_pagina(1))
    btn_siguiente.grid(row=0, column=1)

    cargar_datos_tabla()

def cambiar_estado(rut):
    """ Cambia el estado del administrador dado un rut """
    admin = buscar_admin_por_rut(rut)
    nuevo_estado = not admin[6]  # Cambiar el estado booleano
    editar_admin(rut, nuevo_estado)
    messagebox.showinfo("Estado actualizado", f"El estado del administrador {rut} se ha actualizado.")
    cargar_datos_tabla()  # Recargar la tabla
