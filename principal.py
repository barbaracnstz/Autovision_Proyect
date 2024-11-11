import re
from datetime import datetime
from ultralytics import YOLO
import cv2
import numpy as np
import pytesseract
import psycopg2
from sort.sort import *
from util import obtener_auto, leer_patente, crear_csv
import tkinter as tk
from PIL import Image, ImageTk
import inicio_sesion  # Importa el archivo de inicio de sesión
from tkinter import ttk
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta, timezone

# Ruta de Tesseract en tu sistema (ajustar según corresponda)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Conexión a la base de datos PostgreSQL
conexion_db = psycopg2.connect(
    host="localhost",
    database="autovision",
    user="postgres",
    password="holanda123."
)
cursor_db = conexion_db.cursor()

# Diccionario para almacenar resultados
resultados = {}
seguimiento_motos = Sort()

# Cargar Modelos YOLO
detector_patente = YOLO('best.pt')

# Capturar Video desde la Webcam
cap = cv2.VideoCapture(1)

# Verificar si la cámara se ha abierto correctamente
if not cap.isOpened():
    print("Error al abrir la cámara.")
    exit()

n_frame = 0  # Contador de fotogramas
ret = True

# Inicializar id_seguimiento como una matriz vacía
id_seguimiento = np.empty((0, 5))

def validar_formato_patente(patente):
    """Valida el formato de la patente chilena."""
    patente = patente.upper()
    
    # Corrección de posibles confusiones solo en los dos dígitos centrales
    if len(patente) == 6:
        # Corregir confusiones en los dos caracteres centrales
        centro = patente[2:4].replace('2', 'Z').replace('1', 'L').replace('I', 'J').replace('6', '0')
        
        # Verificar si ambos caracteres centrales son alfabéticos o numéricos
        if (centro[0].isalpha() and centro[1].isalpha()) or (centro[0].isdigit() and centro[1].isdigit()):
            patente = patente[:2] + centro + patente[4:]
        else:
            # Si hay una combinación no válida, retornamos None
            return None
    
    # Verificación final de que el formato cumpla con las reglas
    patron = re.compile(r'^[A-Z]{2}[A-Z0-9]{2}\d{2}$')
    return patente if patron.match(patente) else None

def consultar_residente(patente):
    """Consulta los datos del residente según la patente."""
    query = """
    SELECT r.nombre_residente, r.apellido_residente, r.no_depto_residente, r.telefono_residente, v.patente_vehiculo 
    FROM vehiculo v
    JOIN residente r ON v.residente_rut_residente = r.rut_residente
    WHERE v.patente_vehiculo = %s
    """
    
    cursor_db.execute(query, (patente,))
    resultado = cursor_db.fetchone()
    
    if resultado:
        return {
            "nombre_residente": resultado[0],
            "apellido_residente": resultado[1],
            "no_depto_residente": resultado[2],
            "telefono_residente": resultado[3],
            "patente_vehiculo": resultado[4]
        }
    return None

def mostrar_datos_residente(residente):
    etiqueta_estado.config(text="RESIDENTE", font=("Arial", 36, "bold"))
    etiqueta_nombre.config(text=f"Nombre: {residente['nombre_residente']}")
    etiqueta_apellido.config(text=f"Apellido: {residente['apellido_residente']}")
    etiqueta_depto.config(text=f"Nro depto: {residente['no_depto_residente']}")
    etiqueta_telefono.config(text=f"Teléfono: {residente['telefono_residente']}")
    etiqueta_patente.config(text=f"Patente: {residente['patente_vehiculo']}")

def ocultar_datos_residente():
    etiqueta_estado.config(text="VISITA", font=("Arial", 36, "bold"))
    etiqueta_nombre.config(text="")
    etiqueta_apellido.config(text="")
    etiqueta_depto.config(text="")
    etiqueta_telefono.config(text="")
    etiqueta_patente.config(text="")

def mostrar_sin_detecciones():
    etiqueta_estado.config(text="SIN DETECCIONES", font=("Arial", 24, "bold"))
    etiqueta_nombre.config(text="")
    etiqueta_apellido.config(text="")
    etiqueta_depto.config(text="")
    etiqueta_telefono.config(text="")
    etiqueta_patente.config(text="")

def mostrar_formulario_visita():
    # Ocultar el frame de datos del residente
    frame_datos.place_forget()
    
    # Mostrar los campos del formulario para registrar la visita en el espacio del frame de datos
    frame_formulario_visita.place(relx=0.05, rely=0.15, relwidth=0.3, relheight=0.70)

    boton_registrar_visita.place_forget()

    # Mostrar el botón "Volver" para cerrar el formulario de visita
    boton_volver.place(relx=0.5, rely=0.82)

def volver():
    # Ocultar el formulario de visita
    frame_formulario_visita.place_forget()

    # Volver a mostrar los datos del residente
    frame_datos.place(relx=0.05, rely=0.15, relwidth=0.25, relheight=0.5)

    # Mostrar nuevamente el botón "Registrar Visita"
    boton_registrar_visita.place(relx=0.10, rely=0.77)

    # Ocultar el botón "Volver"
    boton_volver.place_forget()


def completar_rut_residente():
    no_depto_dueno = input_no_depto_dueno.get()
    if not no_depto_dueno:
        messagebox.showerror("Error", "Por favor ingrese un número de departamento.")
        return

    try:
        query = "SELECT rut_residente FROM residente WHERE no_depto_residente = %s"
        cursor_db.execute(query, (no_depto_dueno,))
        resultado = cursor_db.fetchone()

        if resultado:
            rut_residente = resultado[0]
            input_rut_residente.delete(0, tk.END)
            input_rut_residente.insert(0, rut_residente)
        else:
            messagebox.showwarning("Depto no encontrado", f"No se encontró un residente asociado al departamento {no_depto_dueno}.")

    except psycopg2.DatabaseError as e:
        print("Error al consultar residente:", e)
        conexion_db.rollback()

def mostrar_video():
    global n_frame, resultados

    # Leer cada fotograma del video
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el fotograma.")
        return

    n_frame += 1
    resultados[n_frame] = {}

    # Detección de Patentes
    detector_patentes = detector_patente(frame)[0]
    deteccion_encontrada = False
    for patente in detector_patentes.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = patente
        if score > 0.5:
            deteccion_encontrada = True
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
            recorte_patente = frame[int(y1):int(y2), int(x1):int(x2), :]
            recorte_patente_gris = cv2.cvtColor(recorte_patente, cv2.COLOR_BGR2GRAY)
            texto_patente = pytesseract.image_to_string(recorte_patente_gris, config='--psm 8').strip()
            texto_patente = ''.join(filter(str.isalnum, texto_patente))
            texto_patente = validar_formato_patente(texto_patente)

            if texto_patente:
                residente_info = consultar_residente(texto_patente)
                if residente_info:
                    mostrar_datos_residente(residente_info)  # Muestra los datos del residente
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f'Residente: {texto_patente}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    ocultar_datos_residente()  # Oculta los datos y muestra "Visita"
                    cv2.putText(frame, f'Visita: {texto_patente}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if not deteccion_encontrada:
        mostrar_sin_detecciones()

    # Mostrar la fecha y la hora
    fecha_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    (alto_frame, ancho_frame) = frame.shape[:2]
    cv2.putText(frame, fecha_hora, (ancho_frame - 250, alto_frame - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Convertir el fotograma a formato adecuado y mostrar en la ventana de Tkinter
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img_tk = ImageTk.PhotoImage(image=img)
    label_video.imgtk = img_tk
    label_video.configure(image=img_tk)

    # Llamar a esta función nuevamente
    label_video.after(10, mostrar_video)

# Crea la ventana principal
ventana = tk.Tk()
ventana.title("Autovision - Principal")
ventana.geometry(f"{ventana.winfo_screenwidth()}x{ventana.winfo_screenheight()}+0+0")

# Función ajustada para guardar la visita
def guardar_visita():
    rut_visita = input_rut_visita.get()
    dv_visita = input_dv_visita.get()
    nombre_visita = input_nombre_visita.get()
    apellido_visita = input_apellido_visita.get()
    no_depto_dueno = input_no_depto_dueno.get()
    patente_visita = input_patente_visita.get()
    estacionamiento_designado = combo_estacionamiento.get()  # Obtener el valor seleccionado del ComboBox
    momento_ingreso = datetime.now(timezone.utc)  # Almacenar la hora actual con zona horaria para evitar problemas de tipo de datetime

    # Consultar el rut_residente basado en el número de departamento
    try:
        query = "SELECT rut_residente FROM residente WHERE no_depto_residente = %s"
        cursor_db.execute(query, (no_depto_dueno,))
        resultado = cursor_db.fetchone()

        if not resultado:
            messagebox.showwarning("Depto no encontrado", f"No se encontró un residente asociado al departamento {no_depto_dueno}.")
            return

        residente_rut_residente = resultado[0]

        # Insertar el registro de la visita en la base de datos
        query = """
        INSERT INTO visita (rut_visita, dv_visita, nombre_visita, apellido_visita, no_depto_dueno, momento_ingreso, momento_salida, patente_visita, residente_rut_residente, estacionamiento_designado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor_db.execute(query, (rut_visita, dv_visita, nombre_visita, apellido_visita, no_depto_dueno, momento_ingreso, momento_ingreso, patente_visita, residente_rut_residente, estacionamiento_designado))
        
        # Actualizar el estado del estacionamiento a 'ocupado' y establecer el momento de ingreso
        query_update_estacionamiento = "UPDATE estacionamiento SET estado = 'ocupado', id_visita = %s, momento_ingreso = %s WHERE numero_estacionamiento = %s"
        cursor_db.execute(query_update_estacionamiento, (rut_visita, momento_ingreso, estacionamiento_designado))

        conexion_db.commit()
        print(f"Visita registrada: {nombre_visita} {apellido_visita}")

        # Ocultar el formulario de visita y volver a mostrar el frame de datos del residente
        frame_formulario_visita.place_forget()
        frame_datos.place(relx=0.05, rely=0.15, relwidth=0.25, relheight=0.5)

        # Actualizar la interfaz de estacionamientos después de guardar la visita
        actualizar_estacionamientos()

    except psycopg2.DatabaseError as e:
        print("Error al guardar la visita:", e)
        conexion_db.rollback()

def actualizar_estacionamientos():
    try:
        # Consultar el estado de los estacionamientos y las visitas asignadas
        query = """
        SELECT numero_estacionamiento, estado, momento_ingreso
        FROM estacionamiento
        """
        cursor_db.execute(query)
        estacionamientos = cursor_db.fetchall()

        # Actualizar las etiquetas de estacionamiento en la interfaz
        for i in range(3):  # Asumimos que hay 3 estacionamientos
            estacionamiento_numero = i + 1
            estacionamiento = next((e for e in estacionamientos if e[0] == estacionamiento_numero), None)

            if estacionamiento:
                numero, estado, momento_ingreso = estacionamiento
                label_estado = estacionamientos_frames[i]["estado"]
                label_tiempo = estacionamientos_frames[i]["tiempo"]

                print(f"Estacionamiento {numero} - Estado: {estado}, Momento Ingreso: {momento_ingreso}")  # Debug

                if estado == 'ocupado' and momento_ingreso:
                    # Calcular el tiempo transcurrido
                    momento_ingreso = momento_ingreso.replace(tzinfo=None)  # Asegurarnos de que sea naive
                    tiempo_transcurrido = datetime.now() - momento_ingreso

                    # Calcular el tiempo restante
                    tiempo_restante = max(0, 120 - tiempo_transcurrido.total_seconds())  # Tiempo restante en segundos
                    minutos, segundos = divmod(int(tiempo_restante), 60)

                    if tiempo_restante > 0:
                        label_estado.config(text="Ocupado", bg="red")
                        label_tiempo.config(text=f"Tiempo restante: {minutos}:{segundos:02d}")
                    else:
                        # Cambiar el estado a libre si el tiempo restante es cero
                        label_estado.config(text="Libre", bg="lightgreen")
                        label_tiempo.config(text="")
                        liberar_estacionamiento_manual(estacionamiento_numero)  # Liberar automáticamente

                else:
                    label_estado.config(text="Libre", bg="lightgreen")
                    label_tiempo.config(text="")

            else:
                # Si el estacionamiento no está asignado, se considera libre
                estacionamientos_frames[i]["estado"].config(
                    text="Libre",
                    bg="lightgreen"
                )
                estacionamientos_frames[i]["tiempo"].config(text="")

    except psycopg2.DatabaseError as e:
        print("Error al actualizar estacionamientos:", e)
        conexion_db.rollback()

    # Llamar a esta función nuevamente después de 1 segundo
    ventana.after(1000, actualizar_estacionamientos)



# Definir la función para ir al inicio de sesión
def ir_a_inicio_sesion():
    """Cerrar la ventana principal y abrir la ventana de inicio de sesión."""
    ventana.destroy()  # Cierra la ventana principal
    inicio_sesion.abrir_ventana_inicio()  # Abre la ventana de inicio de sesión

# Cargar la imagen de fondo
fondo = Image.open("Fondo2.png").resize((ventana.winfo_screenwidth(), ventana.winfo_screenheight()))
fondo_imagen = ImageTk.PhotoImage(fondo)

# Crear un canvas para el fondo
canvas = tk.Canvas(ventana, width=ventana.winfo_screenwidth(), height=ventana.winfo_screenheight())
canvas.create_image(0, 0, anchor="nw", image=fondo_imagen)
canvas.pack()

# Crear un frame para los datos del residente a la izquierda
frame_datos = tk.Frame(ventana, bg="white", relief="solid", bd=2)
frame_datos.place(relx=0.10, rely=0.15, relwidth=0.2, relheight=0.4)

# Etiquetas para mostrar la información del residente
etiqueta_estado = tk.Label(frame_datos, text="SIN DETECCIONES", font=("Arial", 24, "bold"), bg="white", fg="#696969")
etiqueta_estado.pack(pady=10)

etiqueta_nombre = tk.Label(frame_datos, text="", font=("Arial", 14), bg="white", fg="#4B0082")
etiqueta_nombre.pack(pady=5, anchor="w", padx=10)

etiqueta_apellido = tk.Label(frame_datos, text="", font=("Arial", 14), bg="white", fg="#4B0082")
etiqueta_apellido.pack(pady=5, anchor="w", padx=10)

etiqueta_depto = tk.Label(frame_datos, text="", font=("Arial", 14), bg="white", fg="#4B0082")
etiqueta_depto.pack(pady=5, anchor="w", padx=10)

etiqueta_telefono = tk.Label(frame_datos, text="", font=("Arial", 14), bg="white", fg="#4B0082")
etiqueta_telefono.pack(pady=5, anchor="w", padx=10)

etiqueta_patente = tk.Label(frame_datos, text="", font=("Arial", 14), bg="white", fg="#4B0082")
etiqueta_patente.pack(pady=5, anchor="w", padx=10)

# Crear el frame para el formulario de visita (oculto inicialmente)
frame_formulario_visita = tk.Frame(ventana, bg="gray83", relief="solid", bd=2)

etiqueta_formulario_patente = tk.Label(frame_formulario_visita, text="Patente Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
etiqueta_formulario_patente.pack(pady=5, anchor="w", padx=10)

input_patente_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
input_patente_visita.pack(pady=10, anchor="w", padx=10)

etiqueta_formulario_rut = tk.Label(frame_formulario_visita, text="RUT Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
etiqueta_formulario_rut.pack(pady=5, anchor="w", padx=10)

input_rut_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
input_rut_visita.pack(pady=5, anchor="w", padx=10)

etiqueta_formulario_dv = tk.Label(frame_formulario_visita, text="Dígito Verificador Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
etiqueta_formulario_dv.pack(pady=5, anchor="w", padx=10)

input_dv_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
input_dv_visita.pack(pady=5, anchor="w", padx=10)

etiqueta_formulario_nombre = tk.Label(frame_formulario_visita, text="Nombre Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
etiqueta_formulario_nombre.pack(pady=5, anchor="w", padx=10)

input_nombre_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
input_nombre_visita.pack(pady=5, anchor="w", padx=10)

etiqueta_formulario_apellido = tk.Label(frame_formulario_visita, text="Apellido Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
etiqueta_formulario_apellido.pack(pady=5, anchor="w", padx=10)

input_apellido_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
input_apellido_visita.pack(pady=5, anchor="w", padx=10)

etiqueta_formulario_no_depto = tk.Label(frame_formulario_visita, text="Nro Depto Residente: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
etiqueta_formulario_no_depto.pack(pady=5, anchor="w", padx=10)

input_no_depto_dueno = tk.Entry(frame_formulario_visita, font=("Arial", 14))
input_no_depto_dueno.pack(pady=5, anchor="w", padx=10)

boton_guardar_visita = tk.Button(frame_formulario_visita, text="Guardar Visita", command=guardar_visita, font=("Arial", 14), bg="green", fg="white", width=15, height=2)
boton_guardar_visita.pack(pady=12)
boton_guardar_visita.place(relx=0.08, rely=0.82)

# Crear el botón "Volver" que aparece cuando se está en el formulario de visita
boton_volver = tk.Button(frame_formulario_visita, text="Volver", command=volver, font=("Arial", 14), bg="red", fg="white", width=15, height=2)
boton_volver.place_forget()  # Se inicia oculto

# Botón para registrar visita fuera del frame de datos del residente
boton_registrar_visita = tk.Button(ventana, text="Registrar Visita", command=mostrar_formulario_visita, font=("Arial", 18), bg="blue", fg="white", width=20, height=2)
boton_registrar_visita.place(relx=0.10, rely=0.77)

# Crear un label para mostrar el video a la derecha, ajustado proporcionalmente
label_video = tk.Label(ventana)
label_video.place(relx=0.45, rely=0.1, relwidth=0.42, relheight=0.55)

# Crear los bloques de estacionamientos debajo de la cámara
estacionamientos_frame = tk.Frame(ventana, bg="#009cd8")
estacionamientos_frame.place(relx=0.45, rely=0.7, relwidth=0.42, relheight=0.15)


# Crear el frame para el formulario de visita (oculto inicialmente)
frame_formulario_visita = tk.Frame(ventana, bg="gray83", relief="solid", bd=2)

# Etiqueta y campo para patente visita
etiqueta_formulario_patente = tk.Label(frame_formulario_visita, text="Patente Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
etiqueta_formulario_patente.grid(row=0, column=0, padx=10, pady=5, sticky="w")
input_patente_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
input_patente_visita.grid(row=0, column=1, padx=10, pady=5)

# Etiqueta y campo para RUT visita
etiqueta_formulario_rut = tk.Label(frame_formulario_visita, text="RUT Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
etiqueta_formulario_rut.grid(row=1, column=0, padx=10, pady=5, sticky="w")
input_rut_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
input_rut_visita.grid(row=1, column=1, padx=10, pady=5)

# Etiqueta y campo para dígito verificador
etiqueta_formulario_dv = tk.Label(frame_formulario_visita, text="DV Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
etiqueta_formulario_dv.grid(row=2, column=0, padx=10, pady=5, sticky="w")
input_dv_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
input_dv_visita.grid(row=2, column=1, padx=10, pady=5)

# Etiqueta y campo para nombre visita
etiqueta_formulario_nombre = tk.Label(frame_formulario_visita, text="Nombre Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
etiqueta_formulario_nombre.grid(row=3, column=0, padx=10, pady=5, sticky="w")
input_nombre_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
input_nombre_visita.grid(row=3, column=1, padx=10, pady=5)

# Etiqueta y campo para apellido visita
etiqueta_formulario_apellido = tk.Label(frame_formulario_visita, text="Apellido Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
etiqueta_formulario_apellido.grid(row=4, column=0, padx=10, pady=5, sticky="w")
input_apellido_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
input_apellido_visita.grid(row=4, column=1, padx=10, pady=5)

# Etiqueta y campo para número de departamento
etiqueta_formulario_no_depto = tk.Label(frame_formulario_visita, text="Nro Depto:", font=("Arial", 12), bg="gray83", fg="#4B0082")
etiqueta_formulario_no_depto.grid(row=5, column=0, padx=10, pady=5, sticky="w")
input_no_depto_dueno = tk.Entry(frame_formulario_visita, font=("Arial", 12))
input_no_depto_dueno.grid(row=5, column=1, padx=10, pady=5)

# Combobox para seleccionar el estacionamiento
etiqueta_estacionamiento = tk.Label(frame_formulario_visita, text="Estacionamiento:", font=("Arial", 12), bg="gray83", fg="#4B0082")
etiqueta_estacionamiento.grid(row=6, column=0, padx=10, pady=5, sticky="w")

# Crear un ComboBox con los estacionamientos disponibles
estacionamientos_disponibles = ["1", "2", "3"]
combo_estacionamiento = ttk.Combobox(frame_formulario_visita, values=estacionamientos_disponibles, font=("Arial", 12))
combo_estacionamiento.grid(row=6, column=1, padx=10, pady=5)
combo_estacionamiento.set("Seleccionar")  # Establecer un valor predeterminado

# Botón para guardar la visita
boton_guardar_visita = tk.Button(frame_formulario_visita, text="Guardar Visita", command=guardar_visita, font=("Arial", 12), bg="green", fg="white", width=15, height=2)
boton_guardar_visita.grid(row=7, column=0, columnspan=2, pady=15)


from datetime import datetime, timedelta, timezone

# Crear una función para mostrar la información de estacionamientos en la interfaz
def actualizar_estacionamientos():
    try:
        # Consultar el estado de los estacionamientos y las visitas asignadas
        query = """
        SELECT v.estacionamiento_designado, e.estado, v.momento_ingreso
        FROM visita v
        LEFT JOIN estacionamiento e ON v.estacionamiento_designado = e.numero_estacionamiento
        """
        cursor_db.execute(query)
        estacionamientos = cursor_db.fetchall()

        # Actualizar las etiquetas de estacionamiento en la interfaz
        for i in range(3):  # Asumimos que hay 3 estacionamientos
            estacionamiento_numero = i + 1
            estacionamiento = next((e for e in estacionamientos if e[0] == estacionamiento_numero), None)
            
            if estacionamiento:
                numero, estado, momento_ingreso = estacionamiento
                if estado == 'ocupado' and momento_ingreso:
                    # Asegurarse de que ambos datetime sean del mismo tipo
                    if momento_ingreso.tzinfo is None:
                        # Si momento_ingreso es naive, usar datetime.now() sin timezone
                        tiempo_transcurrido = datetime.now() - momento_ingreso
                    else:
                        # Si momento_ingreso tiene timezone, usar datetime.now(timezone.utc)
                        tiempo_transcurrido = datetime.now(timezone.utc) - momento_ingreso

                    # Calcular el tiempo restante
                    tiempo_restante = max(0, 120 - tiempo_transcurrido.total_seconds())  # Tiempo restante en segundos
                    minutos, segundos = divmod(int(tiempo_restante), 60)
                    estacionamientos_labels[i].config(
                        text=f"Estacionamiento {numero} - Ocupado\nTiempo restante: {minutos}:{segundos:02d}",
                        bg="red"
                    )
                else:
                    estacionamientos_labels[i].config(
                        text=f"Estacionamiento {numero} - Libre",
                        bg="lightgreen"
                    )
            else:
                # Si el estacionamiento no está asignado, se considera libre
                estacionamientos_labels[i].config(
                    text=f"Estacionamiento {estacionamiento_numero} - Libre",
                    bg="lightgreen"
                )
        
    except psycopg2.DatabaseError as e:
        print("Error al actualizar estacionamientos:", e)
        conexion_db.rollback()

    # Llamar a esta función nuevamente después de 1 segundo
    ventana.after(1000, actualizar_estacionamientos)



# Crear el frame para los estacionamientos
estacionamientos_frame = tk.Frame(ventana, bg="#009cd8")
estacionamientos_frame.place(relx=0.45, rely=0.7, relwidth=0.42, relheight=0.3)

# Crear frames y etiquetas para los estacionamientos
estacionamientos_frames = []
for i in range(3):
    frame = tk.Frame(estacionamientos_frame, bg="white", relief="solid", bd=2, width=150, height=100)
    frame.grid(row=0, column=i, padx=15, pady=10)
    estacionamientos_frames.append(frame)

    label_numero = tk.Label(frame, text=f"Estacionamiento {i + 1}", font=("Arial", 14, "bold"), bg="white")
    label_numero.pack(pady=5)

    label_estado = tk.Label(frame, text="Libre", font=("Arial", 12), bg="lightgreen", width=10)
    label_estado.pack(pady=5)

    label_tiempo = tk.Label(frame, text="", font=("Arial", 12), bg="white")
    label_tiempo.pack(pady=5)

    # Añadir el botón para marcar salida del estacionamiento
    boton_liberar = tk.Button(frame, text="Marcar Salida",
                              command=lambda i=i: liberar_estacionamiento_manual(i + 1),
                              font=("Arial", 10), bg="yellow", fg="black", width=12, height=1)
    boton_liberar.pack(pady=5)

    # Guardar las etiquetas para actualizar después
    estacionamientos_labels = {
        "estado": label_estado,
        "tiempo": label_tiempo
    }
    estacionamientos_frames[i] = estacionamientos_labels

from datetime import datetime, timezone

# Crear una función para mostrar la información de estacionamientos en la interfaz
def actualizar_estacionamientos():
    try:
        # Consultar el estado de los estacionamientos y las visitas asignadas
        query = """
        SELECT v.estacionamiento_designado, e.estado, v.momento_ingreso
        FROM visita v
        LEFT JOIN estacionamiento e ON v.estacionamiento_designado = e.numero_estacionamiento
        """
        cursor_db.execute(query)
        estacionamientos = cursor_db.fetchall()

        # Actualizar las etiquetas de estacionamiento en la interfaz
        for i in range(3):  # Asumimos que hay 3 estacionamientos
            estacionamiento_numero = i + 1
            estacionamiento = next((e for e in estacionamientos if e[0] == estacionamiento_numero), None)
            
            if estacionamiento:
                numero, estado, momento_ingreso = estacionamiento
                if estado == 'ocupado' and momento_ingreso:
                    # Convertir momento_ingreso a naive si es offset-aware
                    if momento_ingreso.tzinfo is not None:
                        momento_ingreso = momento_ingreso.replace(tzinfo=None)
                    
                    # Calcular el tiempo transcurrido
                    tiempo_transcurrido = datetime.now() - momento_ingreso

                    # Calcular el tiempo restante
                    tiempo_restante = max(0, 120 - tiempo_transcurrido.total_seconds())  # Tiempo restante en segundos
                    minutos, segundos = divmod(int(tiempo_restante), 60)
                    estacionamientos_frames[i]["estado"].config(
                        text="Ocupado",
                        bg="red"
                    )
                    estacionamientos_frames[i]["tiempo"].config(
                        text=f"Tiempo restante: {minutos}:{segundos:02d}"
                    )
                else:
                    estacionamientos_frames[i]["estado"].config(
                        text="Libre",
                        bg="lightgreen"
                    )
                    estacionamientos_frames[i]["tiempo"].config(text="")

            else:
                # Si el estacionamiento no está asignado, se considera libre
                estacionamientos_frames[i]["estado"].config(
                    text="Libre",
                    bg="lightgreen"
                )
                estacionamientos_frames[i]["tiempo"].config(text="")

    except psycopg2.DatabaseError as e:
        print("Error al actualizar estacionamientos:", e)
        conexion_db.rollback()

    # Llamar a esta función nuevamente después de 1 segundo
    ventana.after(1000, actualizar_estacionamientos)

# Actualizar la interfaz de estacionamientos
actualizar_estacionamientos()


# Función para liberar manualmente un estacionamiento
def liberar_estacionamiento_manual(numero_estacionamiento):
    try:
        # Actualizar el estado del estacionamiento en la base de datos
        query_update_estacionamiento = """
        UPDATE estacionamiento
        SET estado = 'libre', id_visita = NULL, momento_ingreso = NULL
        WHERE numero_estacionamiento = %s
        """
        cursor_db.execute(query_update_estacionamiento, (numero_estacionamiento,))
        conexion_db.commit()

        # Actualizar la interfaz después de liberar el estacionamiento
        actualizar_estacionamientos()
        print(f"Estacionamiento {numero_estacionamiento} liberado.")
        
    except psycopg2.DatabaseError as e:
        print("Error al liberar estacionamiento:", e)
        conexion_db.rollback()

# Crear el frame para los estacionamientos
estacionamientos_frame = tk.Frame(ventana, bg="#009cd8")
estacionamientos_frame.place(relx=0.45, rely=0.7, relwidth=0.42, relheight=0.3)

# Crear frames y etiquetas para los estacionamientos
estacionamientos_frames = []
for i in range(3):
    frame = tk.Frame(estacionamientos_frame, bg="white", relief="solid", bd=2, width=150, height=100)
    frame.grid(row=0, column=i, padx=15, pady=10)
    estacionamientos_frames.append(frame)

    label_numero = tk.Label(frame, text=f"Estacionamiento {i + 1}", font=("Arial", 14, "bold"), bg="white")
    label_numero.pack(pady=5)

    label_estado = tk.Label(frame, text="Libre", font=("Arial", 12), bg="lightgreen", width=10)
    label_estado.pack(pady=5)

    label_tiempo = tk.Label(frame, text="", font=("Arial", 12), bg="white")
    label_tiempo.pack(pady=5)

    # Añadir el botón para marcar salida del estacionamiento
    boton_liberar = tk.Button(frame, text="Marcar Salida",
                              command=lambda i=i: liberar_estacionamiento_manual(i + 1),
                              font=("Arial", 10), bg="yellow", fg="black", width=12, height=1)
    boton_liberar.pack(pady=5)

    # Guardar las etiquetas para actualizar después
    estacionamientos_labels = {
        "estado": label_estado,
        "tiempo": label_tiempo
    }
    estacionamientos_frames[i] = estacionamientos_labels


# Botón para ir al inicio de sesión en la parte superior izquierda
boton_inicio_sesion = tk.Button(ventana, text="Iniciar sesión", command=ir_a_inicio_sesion, font=("Arial", 16), bg="red", fg="white")
boton_inicio_sesion.place(relx=0.05, rely=0.05)

# Iniciar la visualización del video
mostrar_video()

# Ejecutar la aplicación
ventana.mainloop()

# Cerrar la conexión a la base de datos
conexion_db.close()
