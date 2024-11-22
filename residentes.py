import tkinter as tk
from tkinter import messagebox
# from bd import conectar, cargar_datos, insertar_residente, editar_residente
from menu import crear_menu
from bd import conectar,cargar_datos, ejecutar_consulta, insertar_residente, actualizar_residente, obtener_residente_por_rut,eliminar_registro
#, obtener_residente_por_rut, actualizar_residente, eliminar_residente
from tkcalendar import DateEntry
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime

def abrir_ventana_residentes():
    ventana_residentes = tk.Toplevel()
    ventana_residentes.title("Residentes - Administrador")

    # Cargar la imagen de fondo
    fondo_img = Image.open("Fondo2.png")
    fondo_img = fondo_img.resize((1570, 800), Image.LANCZOS)  # Cambiar a LANCZOS
    fondo_photo = ImageTk.PhotoImage(fondo_img)

    # Crear un label para la imagen de fondo
    label_fondo = tk.Label(ventana_residentes, image=fondo_photo)
    label_fondo.place(relwidth=1, relheight=1)  # Ajustar a todo el fondo
    # Mantener la referencia a la imagen
    label_fondo.image = fondo_photo  # Necesario para que la imagen no se elimine

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
    # tk.Label(frame_controles, text="Buscar:").grid(row=1, column=0, padx=10)
    # entry_buscar = tk.Entry(frame_controles, width=30)
    # entry_buscar.grid(row=1, column=1, padx=10)
    # Etiqueta de búsqueda con diseño moderno
    
    label_buscar = ctk.CTkLabel(frame_controles, text="Buscar:", font=("Arial", 12))
    label_buscar.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    # Campo de entrada de búsqueda
    entry_buscar = ctk.CTkEntry(frame_controles, width=250, placeholder_text="Ingrese texto para buscar", font=("Arial", 12))
    entry_buscar.grid(row=1, column=1, padx=10, pady=10, sticky="w")


    # Variables para manejar la paginación y búsqueda
    registros_por_pagina = 10
    pagina_actual = 0
    texto_busqueda = ""  # Variable para almacenar el texto de búsqueda

    # Función para abrir el modal de agregar residente
    def abrir_modal_agregar_residente():
        modal = tk.Toplevel()
        modal.configure(bg="#dee8eb")  # Fondo oscuro
        modal.title("Agregar Residente")
         # Título visible dentro de la ventana
        title_label = tk.Label(modal, text="Agregar Residente", font=("Arial", 16, "bold"), fg="black")
        title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")
        # Crear formulario para ingresar los datos
        label_rut = ctk.CTkLabel(modal, text="RUT Residente", font=("Arial", 12), text_color="black", anchor="w")
        label_rut.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Aquí se aplica el borde redondeado a la entrada
        entry_rut = ctk.CTkEntry(modal, font=("Arial", 12), text_color="black", placeholder_text="Ingrese el RUT",
                                border_width=2, corner_radius=10)  # Borde redondeado con corner_radius
        entry_rut.grid(row=1, column=1, padx=10, pady=20)

        # Etiqueta de mensaje de error debajo del campo de entrada
        rut_error = ctk.CTkLabel(modal, text="", text_color="red", font=("Arial", 10))
        rut_error.grid(row=1, column=1, padx=10, pady=(55, 0), sticky="nsew")

        # Función para validar que solo se ingresen dígitos en el campo de rut
        def validar_usuario_input(*args):
            rut = entry_rut.get().replace(".", "").replace("-", "")  # Limpiar puntos y guion
            
            # Verificar si el RUT contiene solo dígitos
            if not rut.isdigit():
                rut_error.configure(text="Solo se permiten números.")
            else:
                # Validar longitud del RUT
                if len(rut) < 7 or len(rut) > 8:
                    rut_error.configure(text="RUT no válido.")
                else:
                    # Validación de RUT chileno sin el dígito verificador
                    try:
                        int_rut = int(rut)
                        if int_rut < 1 or int_rut > 99999999:
                            rut_error.configure(text="RUT no válido.")
                        else:
                            rut_error.configure(text="")  # Si todo está bien, no mostramos ningún mensaje
                    except ValueError:
                        rut_error.configure(text="RUT no válido.")

        # Conectar la validación al campo de texto
        entry_rut.bind("<KeyRelease>", validar_usuario_input)

        
        # DV Residente
        label_dv = ctk.CTkLabel(modal, text="DV Residente", font=("Arial", 12), text_color="black", anchor="w")
        label_dv.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Campo de entrada para el DV
        entry_dv = ctk.CTkEntry(modal, font=("Arial", 12), text_color="black", placeholder_text="Ingrese el DV",
                                border_width=2, corner_radius=10)  # Borde redondeado
        entry_dv.grid(row=2, column=1, padx=10, pady=20)

        # Etiqueta de mensaje de error debajo del campo de entrada
        dv_error = ctk.CTkLabel(modal, text="", text_color="red", font=("Arial", 10))
        dv_error.grid(row=2, column=1, padx=10, pady=(55, 0), sticky="nsew")

        # Función de validación para el DV
        def validar_dv_input(*args):
            dv = entry_dv.get()

            # Verificar si es un solo dígito
            if dv.isdigit() and len(dv) == 1:
                dv_error.configure(text="")  # No hay error
            # Verificar si es solo la letra 'k' o 'K'
            elif len(dv) == 1 and dv.lower() == 'k':
                dv_error.configure(text="")  # No hay error
            # Verificar si hay más de un carácter ingresado
            elif len(dv) > 1:
                entry_dv.delete(0, tk.END)
                dv_error.configure(text="Solo un dígito o 'k'.")
            # Si es un carácter no permitido
            else:
                entry_dv.delete(0, tk.END)
                dv_error.configure(text="Letra no válida.")

        # Conectar la validación al campo de texto
        entry_dv.bind("<KeyRelease>", validar_dv_input)


        # Nombre
        label_nombre = ctk.CTkLabel(modal, text="Nombre", font=("Arial", 12), text_color="black", anchor="w")
        label_nombre.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # Campo de entrada para el Nombre
        entry_nombre = ctk.CTkEntry(modal, font=("Arial", 12), text_color="black", placeholder_text="Ingrese el Nombre",
                                    border_width=2, corner_radius=10)  # Borde redondeado
        entry_nombre.grid(row=3, column=1, padx=10, pady=10)

        # Etiqueta de mensaje de error debajo del campo de entrada
        caracter_error = ctk.CTkLabel(modal, text="", text_color="red", font=("Arial", 10))
        caracter_error.grid(row=3, column=1, padx=10, pady=(55, 0), sticky="nsew")

        # Función para validar que solo se ingresen letras en el campo de nombre
        def validar_caracteres_input(*args):
            texto = entry_nombre.get()

            # Verifica si el texto contiene números
            if any(char.isdigit() for char in texto) and texto.strip() != "":
                entry_nombre.delete(0, tk.END)  # Borra el texto si contiene números
                caracter_error.configure(text="Solo se permiten letras.")  # Muestra el mensaje de error
            else:
                caracter_error.configure(text="")  # Si es válido, no muestra error

        # Conectar la validación al campo de texto
        entry_nombre.bind("<KeyRelease>", validar_caracteres_input)

        # Apellido
        label_apellido = ctk.CTkLabel(modal, text="Apellido", font=("Arial", 12), text_color="black", anchor="w")
        label_apellido.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # Campo de entrada para el Apellido
        entry_apellido = ctk.CTkEntry(modal, font=("Arial", 12), text_color="black", placeholder_text="Ingrese el Apellido",
                                    border_width=2, corner_radius=10)  # Borde redondeado
        entry_apellido.grid(row=4, column=1, padx=10, pady=10)

        # Etiqueta de mensaje de error debajo del campo de entrada
        caracter2_error = ctk.CTkLabel(modal, text="", text_color="red", font=("Arial", 10))
        caracter2_error.grid(row=4, column=1, padx=10, pady=(55, 0), sticky="nsew")

        # Función para validar que solo se ingresen letras en el campo de apellido
        def validar2_caracteres_input(*args):
            texto = entry_apellido.get()

            # Verifica si el texto contiene números
            if any(char.isdigit() for char in texto) and texto.strip() != "":
                entry_apellido.delete(0, tk.END)  # Borra el texto si contiene números
                caracter2_error.configure(text="Solo se permiten letras.")  # Muestra el mensaje de error
            else:
                caracter2_error.configure(text="")  # Si es válido, no muestra error

        # Conectar la validación al campo de texto
        entry_apellido.bind("<KeyRelease>", validar2_caracteres_input)

        # Etiqueta para la Fecha de Nacimiento usando customtkinter
        label_fec_nac = ctk.CTkLabel(modal, text="Fecha Nacimiento", font=("Arial", 12), text_color="black", anchor="w")
        label_fec_nac.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        # Selector de fecha
        entry_fec_nac = DateEntry(modal, date_pattern='dd-mm-yyyy')  # Puedes cambiar el formato de fecha
        entry_fec_nac.grid(row=5, column=1, padx=10, pady=10)

        # Label para Teléfono
        label_telefono = ctk.CTkLabel(modal, text="Teléfono", font=("Arial", 12), text_color="black", anchor="w")
        label_telefono.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        # Entry para Teléfono
        entry_telefono = ctk.CTkEntry(modal, font=("Arial", 12), text_color="black", placeholder_text="Ingrese Teléfono", 
                                    border_width=2, corner_radius=10)  # Estilo con borde redondeado
        entry_telefono.grid(row=6, column=1, padx=10, pady=10)

        # Etiqueta de mensaje de error debajo del campo de entrada
        telefono_error = ctk.CTkLabel(modal, text="", text_color="red", font=("Arial", 10))
        telefono_error.grid(row=6, column=1, padx=10, pady=(55, 0), sticky="nsew")

        # Función para validar que solo se ingresen dígitos en el campo de teléfono
        def validar_telefono_input(*args):
            texto = entry_telefono.get()
            if not texto.isdigit():
                entry_telefono.delete(0, ctk.END)
                telefono_error.configure(text="Solo se permiten números.")
            elif len(texto) > 8:
                entry_telefono.delete(8, ctk.END)
                telefono_error.configure(text="Máximo 8 números permitidos.")
            else:
                telefono_error.configure(text="")

        # Conectar la validación al campo de texto
        entry_telefono.bind("<KeyRelease>", validar_telefono_input)



        # Label para Nº Departamento
        label_no_depto = ctk.CTkLabel(modal, text="Nº Departamento", font=("Arial", 12), text_color="black", anchor="w")
        label_no_depto.grid(row=7, column=0, padx=10, pady=10, sticky="w")

        # Entry para Nº Departamento
        entry_no_depto = ctk.CTkEntry(modal, font=("Arial", 12), text_color="black", placeholder_text="Ingrese Nº Departamento", 
                                    border_width=2, corner_radius=10)  # Estilo con borde redondeado
        entry_no_depto.grid(row=7, column=1, padx=10, pady=10)

        # Etiqueta de mensaje de error debajo del campo de entrada
        no_depto_error = ctk.CTkLabel(modal, text="", text_color="red", font=("Arial", 10))
        no_depto_error.grid(row=7, column=1, padx=10, pady=(40, 0), sticky="w")

        # Función para validar que solo se ingresen dígitos en el campo de nº departamento
        def validar_no_depto_input(*args):
            texto = entry_no_depto.get()
            if not texto.isdigit():
                entry_no_depto.delete(0, ctk.END)
                no_depto_error.configure(text="Solo se permiten números.")
            elif len(texto) > 4:
                entry_no_depto.delete(4, ctk.END)
                no_depto_error.configure(text="Máximo 4 números permitidos.")
            else:
                no_depto_error.configure(text="")

        # Conectar la validación al campo de texto
        entry_no_depto.bind("<KeyRelease>", validar_no_depto_input)

        # Etiqueta para la Patente de Vehículo usando customtkinter
        label_patente = ctk.CTkLabel(modal, text="Patente Vehículo", font=("Arial", 12), text_color="black", anchor="w")
        label_patente.grid(row=8, column=0, padx=10, pady=10, sticky="w")

        # Entrada para la patente usando customtkinter
        entry_patente = ctk.CTkEntry(modal, font=("Arial", 12), text_color="black", placeholder_text="Ingrese la patente", 
                                    border_width=2, corner_radius=10)  # Borde redondeado
        entry_patente.grid(row=8, column=1, padx=10, pady=10)

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
        # btn_guardar = tk.Button(modal, text="Guardar", command=guardar_residente)
        # btn_guardar.grid(row=9, column=0, columnspan=2, pady=10)
        btn_guardar = ctk.CTkButton(modal, text="Guardar", command=guardar_residente, 
                            fg_color="#007BFF", hover_color="#0056b3", font=("Arial", 12, "bold"))
        btn_guardar.grid(row=9, column=0, columnspan=2, pady=10)
    def editar_registro(rut):
        # Obtener datos del residente usando el RUT
        residente = obtener_residente_por_rut(rut)  # Asegúrate de que esta función esté implementada en bd.py

        if not residente:
            messagebox.showerror("Error", "No se encontró el residente.")
            return

        # Crear un modal para editar el residente
        modal_editar = tk.Toplevel()
        modal_editar.title("Editar Residente")
        modal_editar.configure(bg="#dee8eb")  # Fondo oscuro

        # Crear un título dentro del modal con color azul
        titulo_label = ctk.CTkLabel(modal_editar, text="Editar Residente", font=("Arial", 16, "bold"), text_color="black")
        titulo_label.grid(row=0, column=0, columnspan=2, pady=10)  # Coloca el título en la primera fila, con algo de espacio

        # Mostrar el RUT (solo lectura)
        label_rut = ctk.CTkLabel(modal_editar, text="RUT Residente", font=("Arial", 12), anchor="w")
        label_rut.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        entry_rut = ctk.CTkEntry(modal_editar, font=("Arial", 12),fg_color="#f0f0f0")
        entry_rut.grid(row=1, column=1, padx=10, pady=10)
        entry_rut.insert(0, residente[0])  # Asumiendo que residente[0] es el DV
        entry_rut.configure(state="readonly")

        # Mostrar el DV (solo lectura)
        label_dv = ctk.CTkLabel(modal_editar, text="DV Residente", font=("Arial", 12), anchor="w")
        label_dv.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        entry_dv = ctk.CTkEntry(modal_editar, font=("Arial", 12),fg_color="#f0f0f0")
        entry_dv.grid(row=2, column=1, padx=10, pady=10)
        entry_dv.insert(0, residente[1])  # Asumiendo que residente[1] es el DV
        entry_dv.configure(state="readonly")
        # Mostrar el Nombre (solo lectura)
        label_nombre = ctk.CTkLabel(modal_editar, text="Nombre", font=("Arial", 12), anchor="w")
        label_nombre.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        entry_nombre = ctk.CTkEntry(modal_editar, font=("Arial", 12),fg_color="#f0f0f0")
        entry_nombre.grid(row=3, column=1, padx=10, pady=10)
        entry_nombre.insert(0, residente[2])  # Asumiendo que residente[3] es el Apellido
        entry_nombre.configure(state="readonly")
        # Mostrar el Apellido (solo lectura)
        label_apellido = ctk.CTkLabel(modal_editar, text="Apellido", font=("Arial", 12), anchor="w")
        label_apellido.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        entry_apellido = ctk.CTkEntry(modal_editar, font=("Arial", 12),fg_color="#f0f0f0")
        entry_apellido.grid(row=4, column=1, padx=10, pady=10)
        entry_apellido.insert(0, residente[3])  # Asumiendo que residente[3] es el Apellido
        entry_apellido.configure(state="readonly")

                # Mostrar la Fecha de Nacimiento (solo lectura)
        label_fec_nac = ctk.CTkLabel(modal_editar, text="Fecha Nacimiento", font=("Arial", 12), anchor="w")
        label_fec_nac.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        # Crear el campo de entrada
        entry_fec_nac = ctk.CTkEntry(modal_editar, font=("Arial", 12), fg_color="#f0f0f0")
        entry_fec_nac.grid(row=5, column=1, padx=10, pady=10)

        # Obtener la fecha (asumimos que residente[4] es un objeto datetime o string con formato "YYYY-MM-DD")
        fec_nac = residente[4]  # Por ejemplo, residente[4] es "1990-05-15"

        # Si la fecha es un string, conviértela a un objeto datetime para asegurarte de que tenga el formato correcto
        if isinstance(fec_nac, str):
            fec_nac = datetime.strptime(fec_nac, "%Y-%m-%d")  # Convierte de "YYYY-MM-DD" a objeto datetime

        # Formatear la fecha como "DD-MM-YY"
        fec_nac_formateada = fec_nac.strftime("%d-%m-%y")  # El formato es DD-MM-YY

        # Insertar la fecha en el campo de entrada
        entry_fec_nac.insert(0, fec_nac_formateada)

        # Hacer el campo de solo lectura
        entry_fec_nac.configure(state="readonly")
        # # Mostrar la Fecha de Nacimiento (solo lectura)
        # label_fec_nac = ctk.CTkLabel(modal_editar, text="Fecha Nacimiento", font=("Arial", 12), anchor="w")
        # label_fec_nac.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        # entry_fec_nac = ctk.CTkEntry(modal_editar, font=("Arial", 12),fg_color="#f0f0f0")
        # entry_fec_nac.grid(row=5, column=1, padx=10, pady=10)
        # entry_fec_nac.insert(0, residente[4])  # Asumiendo que residente[4] es la Fecha de Nacimiento
        # entry_fec_nac.configure(state="readonly")
        # Campo editable para el Teléfono
        label_telefono = ctk.CTkLabel(modal_editar, text="Teléfono", font=("Arial", 12), anchor="w")
        label_telefono.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        entry_telefono = ctk.CTkEntry(modal_editar, font=("Arial", 12))
        entry_telefono.grid(row=6, column=1, padx=10, pady=10)
        entry_telefono.insert(0, residente[5])  # Asumiendo que residente[5] es el Teléfono

        # Etiqueta de error para el Teléfono
        telefono_error = ctk.CTkLabel(modal_editar, text="", fg_color="transparent", text_color="red", font=("Arial", 10))
        telefono_error.grid(row=6, column=1, padx=10, pady=(55, 0), sticky="nsew")  # Ajustamos aquí

        def validar_telefono_input(*args):
            texto = entry_telefono.get()
            if not texto.isdigit():
                entry_telefono.delete(0, ctk.END)
                telefono_error.configure(text="Solo se permiten números.")
            elif len(texto) > 8:
                entry_telefono.delete(8, ctk.END)
                telefono_error.configure(text="Máximo 8 números permitidos.")
            else:
                telefono_error.configure(text="")

        entry_telefono.bind("<KeyRelease>", validar_telefono_input)



        # Campo editable para el Nº Departamento
        label_no_depto = ctk.CTkLabel(modal_editar, text="Nº Departamento", font=("Arial", 12))
        label_no_depto.grid(row=7, column=0, padx=10, pady=10)

        entry_no_depto = ctk.CTkEntry(modal_editar)
        entry_no_depto.grid(row=7, column=1, padx=10, pady=10)
        entry_no_depto.insert(0, residente[6])  # Asumiendo que residente[6] es el Nº Departamento

        # Etiqueta de error para el Nº Departamento
        no_depto_error = ctk.CTkLabel(modal_editar, text="", fg_color="transparent", text_color="red", font=("Arial", 10))
        no_depto_error.grid(row=7, column=1, padx=60, pady=(55, 0), sticky="nsew")  # Ajustamos aquí

        def validar_no_depto_input(*args):
            texto = entry_no_depto.get()
            if not texto.isdigit():
                entry_no_depto.delete(0, tk.END)
                no_depto_error.configure(text="Solo se permiten números.")
            elif len(texto) > 4:
                entry_no_depto.delete(4, tk.END)
                no_depto_error.configure(text="Máximo 4 números permitidos.")
            else:
                no_depto_error.configure(text="")

        # Conectar la validación al campo de texto
        entry_no_depto.bind("<KeyRelease>", validar_no_depto_input)

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

        # # Botón para guardar cambios
        # btn_guardar = tk.Button(modal_editar, text="Guardar Cambios", command=guardar_cambios_residente)
        # btn_guardar.grid(row=7, column=0, columnspan=2, pady=10)
        # Botón para guardar cambios con color azul
        btn_guardar = ctk.CTkButton(modal_editar, text="Guardar Cambios", command=guardar_cambios_residente, 
                                    fg_color="#007bff", hover_color="#0056b3", font=("Arial", 12, "bold"),text_color="white")
        btn_guardar.grid(row=8, column=0, columnspan=2, pady=10)



    # Crear botón "Agregar residente"
    # btn_agregar_residente = tk.Button(ventana_residentes, text="Agregar Residente", command=abrir_modal_agregar_residente)
    # btn_agregar_residente.pack(pady=20)
    # Botón "Agregar Residente"
    btn_agregar_residente = ctk.CTkButton(
        ventana_residentes,
        text="Agregar Residente",
        command=abrir_modal_agregar_residente,
        fg_color="#2ecc71",  # Color de fondo verde
        hover_color="lightgreen",  # Color cuando el mouse pasa por encima (verde más claro)
        text_color="white",  # Color de las letras blancas
        font=("Arial", 14, "bold")  # Mismo tamaño y fuente que los anteriores (Arial, 14, negrita)
    )
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
            label = tk.Label(frame_tabla, text=encabezado, font=('Arial', 10, 'bold'), bg="#3498db",borderwidth=1, relief="solid", width=15)
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
                label = tk.Label(frame_tabla, text=dato, borderwidth=1, bg="white",relief="solid", width=15)
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
            btn_anterior.configure(state="normal")
        else:
            btn_anterior.configure(state="disabled")

        # Verificar si hay una página siguiente
        if (pagina_actual + 1) * registros_por_pagina < total_registros:
            btn_siguiente.configure(state="normal")
        else:
            btn_siguiente.configure(state="disabled")

    # Crear la tabla de datos
    frame_tabla = tk.Frame(ventana_residentes)
    frame_tabla.pack(pady=20)

    # Encabezados de la tabla
    encabezados = ["RUT", "Nombre", "Teléfono", "Depto", "Patente", "Acción", "Acción"]

    # Crear los botones de paginación
    frame_paginacion = tk.Frame(ventana_residentes)
    frame_paginacion.pack(pady=20)

    # btn_anterior = tk.Button(frame_paginacion, text="Anterior", command=lambda: cambiar_pagina(-1))
    # btn_anterior.grid(row=0, column=0)

    # btn_siguiente = tk.Button(frame_paginacion, text="Siguiente", command=lambda: cambiar_pagina(1))
    # btn_siguiente.grid(row=0, column=1)
    # Botón "Anterior"
    btn_anterior = ctk.CTkButton(
        frame_paginacion,
        text="Anterior",
        command=lambda: cambiar_pagina(-1),
        fg_color="blue",  # Color de fondo del botón
        hover_color="lightblue",  # Color cuando se pasa el mouse por encima
        text_color="white",  # Color del texto (letras blancas)
        font=("Arial", 14, "bold")  # Fuente del texto, puedes cambiarla
    )
    btn_anterior.grid(row=0, column=0, padx=10, pady=5)

    

    # Botón "Siguiente"
    btn_siguiente = ctk.CTkButton(
        frame_paginacion,
        text="Siguiente",
        command=lambda: cambiar_pagina(1),
        fg_color="blue",  # Color de fondo del botón
        hover_color="lightblue",  # Color cuando se pasa el mouse por encima
        text_color="white",  # Color del texto (letras blancas)
        font=("Arial", 14, "bold")  # Fuente del texto
    )
    btn_siguiente.grid(row=0, column=1, padx=10, pady=5)
    
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
