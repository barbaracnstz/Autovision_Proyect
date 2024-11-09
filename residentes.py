import tkinter as tk
from tkinter import messagebox
# from bd import conectar, cargar_datos, insertar_residente, editar_residente
from menu import crear_menu
from bd import conectar,cargar_datos, ejecutar_consulta, insertar_residente, actualizar_residente, obtener_residente_por_rut
#, obtener_residente_por_rut, actualizar_residente, eliminar_residente



def abrir_ventana_residentes():
    ventana_residentes = tk.Toplevel()
    ventana_residentes.title("Residentes - Administrador")

    # Obtener el tamaño de la pantalla y ajustar la ventana
    ancho_ventana = ventana_residentes.winfo_screenwidth()
    alto_ventana = ventana_residentes.winfo_screenheight()
    ventana_residentes.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")

    # Calcular el centro de la pantalla
    ancho_pantalla = ventana_residentes.winfo_screenwidth()
    alto_pantalla = ventana_residentes.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    y = (alto_pantalla // 2) - (alto_ventana // 2)

    # Establecer la geometría de la ventana para centrarla
    ventana_residentes.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    # Crear el menú
    crear_menu(ventana_residentes)

    # Crear un Frame para los controles (barra de búsqueda y paginación)
    frame_controles = tk.Frame(ventana_residentes)
    frame_controles.pack(pady=20)

    label_titulo = tk.Label(frame_controles, text="Lista de Residentes", font=("Arial", 14, "bold"))
    label_titulo.grid(row=0, column=0, columnspan=2, pady=10)

    # Crear barra de búsqueda
    tk.Label(frame_controles, text="Buscar:").grid(row=1, column=0, padx=10)
    entry_buscar = tk.Entry(frame_controles, width=30)
    entry_buscar.grid(row=1, column=1, padx=10)

    # Variables para manejar la paginación y búsqueda
    registros_por_pagina = 10
    pagina_actual = 0
    texto_busqueda = ""  # Variable para almacenar el texto de búsqueda

    # Función para abrir el modal de agregar residente
    def abrir_modal_agregar_residente():
        modal = tk.Toplevel()
        modal.title("Agregar Residente")

        # Crear formulario para ingresar los datos
        label_rut = tk.Label(modal, text="RUT Residente")
        label_rut.grid(row=0, column=0, padx=10, pady=10)
        entry_rut = tk.Entry(modal)
        entry_rut.grid(row=0, column=1, padx=10)

        label_dv = tk.Label(modal, text="DV Residente")
        label_dv.grid(row=1, column=0, padx=10)
        entry_dv = tk.Entry(modal)
        entry_dv.grid(row=1, column=1, padx=10)

        label_nombre = tk.Label(modal, text="Nombre")
        label_nombre.grid(row=2, column=0, padx=10)
        entry_nombre = tk.Entry(modal)
        entry_nombre.grid(row=2, column=1, padx=10)

        label_apellido = tk.Label(modal, text="Apellido")
        label_apellido.grid(row=3, column=0, padx=10)
        entry_apellido = tk.Entry(modal)
        entry_apellido.grid(row=3, column=1, padx=10)

        label_fec_nac = tk.Label(modal, text="Fecha Nacimiento")
        label_fec_nac.grid(row=4, column=0, padx=10)
        entry_fec_nac = tk.Entry(modal)
        entry_fec_nac.grid(row=4, column=1, padx=10)

        label_telefono = tk.Label(modal, text="Teléfono")
        label_telefono.grid(row=5, column=0, padx=10)
        entry_telefono = tk.Entry(modal)
        entry_telefono.grid(row=5, column=1, padx=10)

        label_no_depto = tk.Label(modal, text="Nº Departamento")
        label_no_depto.grid(row=6, column=0, padx=10)
        entry_no_depto = tk.Entry(modal)
        entry_no_depto.grid(row=6, column=1, padx=10)

        label_patente = tk.Label(modal, text="Patente Vehículo")
        label_patente.grid(row=7, column=0, padx=10)
        entry_patente = tk.Entry(modal)
        entry_patente.grid(row=7, column=1, padx=10)

        def guardar_residente():
            # Obtener los datos ingresados en el formulario
            rut = entry_rut.get()
            dv = entry_dv.get()
            nombre = entry_nombre.get()
            apellido = entry_apellido.get()
            fecha_nac = entry_fec_nac.get()
            telefono = entry_telefono.get()
            no_depto = entry_no_depto.get()
            patente = entry_patente.get()

            # Verificar que todos los campos estén llenos
            if not (rut and dv and nombre and apellido and fecha_nac and telefono and no_depto and patente):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            # Llamar a la función insertar_residente de bd.py para agregar el nuevo residente
            try:
                insertar_residente(rut, dv, nombre, apellido, fecha_nac, telefono, no_depto, patente)
                messagebox.showinfo("Éxito", "Residente agregado correctamente.")
                modal.destroy()  # Cerrar la ventana modal después de guardar
                cargar_datos_tabla()  # Actualizar la tabla de residentes
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar el residente: {str(e)}")



        # Botón para guardar
        btn_guardar = tk.Button(modal, text="Guardar", command=guardar_residente)
        btn_guardar.grid(row=8, column=0, columnspan=2, pady=10)
        
    def editar_registro(rut):
        # Obtener datos del residente usando el RUT
        residente = obtener_residente_por_rut(rut)  # Asegúrate de que esta función esté implementada en bd.py

        if not residente:
            messagebox.showerror("Error", "No se encontró el residente.")
            return

        # Crear un modal para editar el residente
        modal_editar = tk.Toplevel()
        modal_editar.title("Editar Residente")

        # Mostrar el RUT (solo lectura)
        label_rut = tk.Label(modal_editar, text="RUT Residente")
        label_rut.grid(row=0, column=0, padx=10, pady=10)
        entry_rut = tk.Entry(modal_editar, state="readonly")
        entry_rut.grid(row=0, column=1, padx=10)
        entry_rut.insert(0, residente[0])  # Asumiendo que residente[0] es el RUT

        # Mostrar el DV (solo lectura)
        label_dv = tk.Label(modal_editar, text="DV Residente")
        label_dv.grid(row=1, column=0, padx=10)
        entry_dv = tk.Entry(modal_editar, state="readonly")
        entry_dv.grid(row=1, column=1, padx=10)
        entry_dv.insert(0, residente[1])  # Asumiendo que residente[1] es el DV

        # Mostrar el Nombre (solo lectura)
        label_nombre = tk.Label(modal_editar, text="Nombre")
        label_nombre.grid(row=2, column=0, padx=10)
        entry_nombre = tk.Entry(modal_editar, state="readonly")
        entry_nombre.grid(row=2, column=1, padx=10)
        entry_nombre.insert(0, residente[2])  # Asumiendo que residente[2] es el Nombre

        # Mostrar el Apellido (solo lectura)
        label_apellido = tk.Label(modal_editar, text="Apellido")
        label_apellido.grid(row=3, column=0, padx=10)
        entry_apellido = tk.Entry(modal_editar, state="readonly")
        entry_apellido.grid(row=3, column=1, padx=10)
        entry_apellido.insert(0, residente[3])  # Asumiendo que residente[3] es el Apellido

        # Mostrar la Fecha de Nacimiento (solo lectura)
        label_fec_nac = tk.Label(modal_editar, text="Fecha Nacimiento")
        label_fec_nac.grid(row=4, column=0, padx=10)
        entry_fec_nac = tk.Entry(modal_editar, state="readonly")
        entry_fec_nac.grid(row=4, column=1, padx=10)
        entry_fec_nac.insert(0, residente[4])  # Asumiendo que residente[4] es la Fecha de Nacimiento

        # Campo editable para el Teléfono
        label_telefono = tk.Label(modal_editar, text="Teléfono")
        label_telefono.grid(row=5, column=0, padx=10)
        entry_telefono = tk.Entry(modal_editar)
        entry_telefono.grid(row=5, column=1, padx=10)
        entry_telefono.insert(0, residente[5])  # Asumiendo que residente[5] es el Teléfono

        # Campo editable para el Nº Departamento
        label_no_depto = tk.Label(modal_editar, text="Nº Departamento")
        label_no_depto.grid(row=6, column=0, padx=10)
        entry_no_depto = tk.Entry(modal_editar)
        entry_no_depto.grid(row=6, column=1, padx=10)
        entry_no_depto.insert(0, residente[6])  # Asumiendo que residente[6] es el Nº Departamento

        # Función para guardar los cambios
        def guardar_cambios_residente():
            nuevo_telefono = entry_telefono.get()
            nuevo_no_depto = entry_no_depto.get()

            # Validar que los campos no estén vacíos
            if not nuevo_telefono or not nuevo_no_depto:
                messagebox.showwarning("Advertencia", "Por favor, complete todos los campos.")
                return

            # Actualizar en la base de datos
            actualizado = actualizar_residente(rut, nuevo_telefono, nuevo_no_depto)  # Asegúrate de que esta función esté implementada en bd.py
            if actualizado:
                messagebox.showinfo("Éxito", "Residente actualizado correctamente.")
                modal_editar.destroy()  # Cierra el modal después de guardar
                cargar_datos_tabla()  # Recarga los datos de la tabla principal
            else:
                messagebox.showerror("Error", "No se pudo actualizar el residente.")

        # Botón para guardar cambios
        btn_guardar = tk.Button(modal_editar, text="Guardar Cambios", command=guardar_cambios_residente)
        btn_guardar.grid(row=7, column=0, columnspan=2, pady=10)




    # Crear botón "Agregar residente"
    btn_agregar_residente = tk.Button(ventana_residentes, text="Agregar Residente", command=abrir_modal_agregar_residente)
    btn_agregar_residente.pack(pady=20)

    # Función para actualizar el texto de búsqueda y recargar la tabla
    def actualizar_busqueda(event=None):
        nonlocal texto_busqueda
        texto_busqueda = entry_buscar.get().lower()  # Obtener texto de búsqueda en minúsculas
        cargar_datos_tabla()  # Recargar la tabla con el filtro aplicado

    # Asociar la tecla de búsqueda con la función para actualizar
    entry_buscar.bind("<KeyRelease>", actualizar_busqueda)  # Actualiza la búsqueda al presionar una tecla

    # Función para cargar datos en la tabla con paginación y búsqueda
    def cargar_datos_tabla():
        # Limpiar la tabla antes de cargar nuevos datos
        for widget in frame_tabla.winfo_children():
            widget.grid_forget()

        # Encabezados de la tabla
        for i, encabezado in enumerate(encabezados):
            label = tk.Label(frame_tabla, text=encabezado, font=('Arial', 10, 'bold'), borderwidth=1, relief="solid", width=15)
            label.grid(row=0, column=i, sticky="nsew")

        # Obtener los datos de la base de datos
        registros = cargar_datos()

        # Filtrar los registros si hay texto de búsqueda
        if texto_busqueda:
            registros = [r for r in registros if any(texto_busqueda in str(dato).lower() for dato in r)]

        # Calcular los registros a mostrar para la página actual
        inicio = pagina_actual * registros_por_pagina
        fin = inicio + registros_por_pagina
        registros_pagina = registros[inicio:fin]

        # Añadir datos a la tabla
        for row_num, registro in enumerate(registros_pagina, start=1):
            # RUT, NOMBRE, TELEFONO, NRO DEPTO, PATENTE
            for col_num, dato in enumerate(registro):
                label = tk.Label(frame_tabla, text=dato, borderwidth=1, relief="solid", width=15)
                label.grid(row=row_num, column=col_num, sticky="nsew")

            # Botón EDITAR
            btn_editar = tk.Button(frame_tabla, text="EDITAR", bg="yellow", command=lambda rut=registro[0]: editar_registro(rut))
            btn_editar.grid(row=row_num, column=5, sticky="nsew")


            # Botón ELIMINAR
            btn_eliminar = tk.Button(frame_tabla, text="ELIMINAR", bg="red", fg="white", command=lambda rut=registro[0]: eliminar_registro(rut))
            btn_eliminar.grid(row=row_num, column=6, sticky="nsew")

        # Actualizar botones de paginación
        actualizar_botones_paginacion(len(registros))

    # Función para actualizar los botones de paginación
    def actualizar_botones_paginacion(total_registros):
        # Verificar si hay una página anterior
        if pagina_actual > 0:
            btn_anterior.config(state="normal")
        else:
            btn_anterior.config(state="disabled")

        # Verificar si hay una página siguiente
        if (pagina_actual + 1) * registros_por_pagina < total_registros:
            btn_siguiente.config(state="normal")
        else:
            btn_siguiente.config(state="disabled")

    # Crear la tabla de datos
    frame_tabla = tk.Frame(ventana_residentes)
    frame_tabla.pack(pady=20)

    # Encabezados de la tabla
    encabezados = ["RUT", "Nombre", "Teléfono", "Depto", "Patente", "Acción", "Acción"]

    # Crear los botones de paginación
    frame_paginacion = tk.Frame(ventana_residentes)
    frame_paginacion.pack(pady=20)

    btn_anterior = tk.Button(frame_paginacion, text="Anterior", command=lambda: cambiar_pagina(-1))
    btn_anterior.grid(row=0, column=0)

    btn_siguiente = tk.Button(frame_paginacion, text="Siguiente", command=lambda: cambiar_pagina(1))
    btn_siguiente.grid(row=0, column=1)

    # Función para cambiar de página
    def cambiar_pagina(direccion):
        nonlocal pagina_actual
        pagina_actual += direccion
        cargar_datos_tabla()

    # Cargar los datos iniciales
    cargar_datos_tabla()

# Si estás ejecutando este script directamente, se ejecutará la siguiente línea:
if __name__ == "__main__":
    abrir_ventana_residentes()
