import tkinter as tk
from tkinter import messagebox
from bd import conectar, editar_residente, cargar_datos, eliminar_residente  # Asegúrate de que cargar_datos esté en bd.py
from menu import crear_menu

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

    # Crear un Frame para centrar la tabla
    frame_tabla = tk.Frame(ventana_residentes)
    frame_tabla.pack(pady=20)

    # Crear encabezados de tabla
    encabezados = ["RUT", "NOMBRE", "TELEFONO", "NRO DEPTO", "PATENTE", "EDITAR", "ELIMINAR"]
    for i, encabezado in enumerate(encabezados):
        label = tk.Label(frame_tabla, text=encabezado, font=('Arial', 10, 'bold'), borderwidth=1, relief="solid", width=15)
        label.grid(row=0, column=i, sticky="nsew")

    # Función para cargar datos en la tabla
    def cargar_datos_tabla():
        # Limpiar la tabla antes de cargar nuevos datos
        for widget in frame_tabla.winfo_children():
            widget.destroy()

        # Recrear encabezados de tabla
        for i, encabezado in enumerate(encabezados):
            label = tk.Label(frame_tabla, text=encabezado, font=('Arial', 10, 'bold'), borderwidth=1, relief="solid", width=15)
            label.grid(row=0, column=i, sticky="nsew")

        # Obtener los datos de la base de datos usando la función en bd.py
        registros = cargar_datos()

        # Añadir datos a la tabla
        for row_num, registro in enumerate(registros, start=1):
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

    # Función para editar un registro
    def editar_registro(rut):
        # Obtener los datos del residente a editar
        query = """SELECT nombre_residente, telefono_residente, no_depto_residente, patente_vehiculo 
                   FROM residente LEFT JOIN vehiculo ON residente.rut_residente = vehiculo.residente_rut_residente 
                   WHERE rut_residente = %s"""
        cursor = conectar().cursor()  # Conexión a la base de datos
        cursor.execute(query, (rut,))
        residente = cursor.fetchone()

        if residente:
            nombre, telefono, nro_depto, patente = residente

            # Crear una ventana modal para editar los datos
            modal_editar = tk.Toplevel(ventana_residentes)
            modal_editar.title("Editar Residente")

            # Campos para editar
            tk.Label(modal_editar, text="Nombre:").grid(row=0, column=0)
            entry_nombre = tk.Entry(modal_editar)
            entry_nombre.insert(0, nombre)
            entry_nombre.grid(row=0, column=1)

            tk.Label(modal_editar, text="Teléfono:").grid(row=1, column=0)
            entry_telefono = tk.Entry(modal_editar)
            entry_telefono.insert(0, telefono)
            entry_telefono.grid(row=1, column=1)

            tk.Label(modal_editar, text="Nro Depto:").grid(row=2, column=0)
            entry_nro_depto = tk.Entry(modal_editar)
            entry_nro_depto.insert(0, nro_depto)
            entry_nro_depto.grid(row=2, column=1)

            tk.Label(modal_editar, text="Patente:").grid(row=3, column=0)
            entry_patente = tk.Entry(modal_editar)
            entry_patente.insert(0, patente)
            entry_patente.grid(row=3, column=1)

            # Botón para guardar cambios
            def guardar_cambios():
                nuevo_nombre = entry_nombre.get()
                nuevo_telefono = entry_telefono.get()
                nuevo_nro_depto = entry_nro_depto.get()
                nueva_patente = entry_patente.get()

                # Llamar a la función editar_residente en bd.py
                try:
                    editar_residente(rut, nuevo_nombre, nuevo_telefono, nuevo_nro_depto, nueva_patente)
                    messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
                    modal_editar.destroy()  # Cerrar la ventana modal
                    cargar_datos_tabla()  # Volver a cargar los datos en la tabla
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar el registro: {e}")

            btn_guardar = tk.Button(modal_editar, text="Guardar", command=guardar_cambios)
            btn_guardar.grid(row=4, columnspan=2)

    def eliminar_registro(rut):
        if messagebox.askyesno("Eliminar", f"¿Está seguro de eliminar el registro de RUT: {rut}?"):
            try:
                eliminar_residente(rut)  # Llama a la función eliminar_residente
                messagebox.showinfo("Eliminar", "Registro eliminado correctamente.")
                cargar_datos()  # Llama a la función que carga los datos nuevamente en la tabla
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el registro: {e}")

    # Cargar datos en la tabla al iniciar la ventana
    cargar_datos_tabla()


    # Añadir datos a la tabla
    for row_num, registro in enumerate(registros, start=1):
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

    # Hacer que las columnas sean del mismo ancho
    for col in range(len(encabezados)):
        frame_tabla.grid_columnconfigure(col, weight=1)

    ventana_residentes.mainloop()
