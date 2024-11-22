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
import random
from PIL import Image, ImageTk
import inicio_sesion  # Importa el archivo de inicio de sesión
from tkinter import ttk
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta, timezone
import customtkinter as ctk


# Ruta de Tesseract en tu sistema (ajustar según corresponda)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Conexión a la base de datos PostgreSQL
conexion_db = psycopg2.connect(
    host="localhost",
    database="autovision",
    user="postgres",
    password="root"
)
cursor_db = conexion_db.cursor()

# Diccionario para almacenar resultados
resultados = {}
seguimiento_motos = Sort()

# Cargar Modelos YOLO
detector_patente = YOLO('best.pt')

# Capturar Video desde la Webcam
cap = cv2.VideoCapture(0)

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

def consultar_visita_historica(patente):
    """Consulta los datos de la visita histórica según la patente."""
    query = """
    SELECT rut_visita_historica, dv_visita_historica, nombre_visita_historica, apellido_visita_historica,
           no_depto_visita_historica, patente_visita_historica, momento_ingreso_historico
    FROM visita_historico
    WHERE patente_visita_historica = %s
    ORDER BY momento_ingreso_historico DESC
    LIMIT 1
    """
    cursor_db.execute(query, (patente,))
    resultado = cursor_db.fetchone()
    
    if resultado:
        return {
            "rut_visita_historica": resultado[0],
            "dv_visita_historica": resultado[1],
            "nombre_visita_historica": resultado[2],
            "apellido_visita_historica": resultado[3],
            "no_depto_visita_historica": resultado[4],
            "patente_visita_historica": resultado[5],
            "momento_ingreso_historico": resultado[6]
        }
    return None

def mostrar_datos_residente(residente):
    etiqueta_estado.config(text="RESIDENTE", font=("Arial", 36, "bold"))
    etiqueta_nombre.config(text=f"Nombre: {residente['nombre_residente']}")
    etiqueta_apellido.config(text=f"Apellido: {residente['apellido_residente']}")
    etiqueta_depto.config(text=f"Nro depto: {residente['no_depto_residente']}")
    etiqueta_telefono.config(text=f"Teléfono: {residente['telefono_residente']}")
    etiqueta_patente.config(text=f"Patente: {residente['patente_vehiculo']}")

def mostrar_datos_visita_historica(visita):
    # Mostrar los datos en la parte izquierda de la ventana
    etiqueta_estado.config(text="VISITA ANTERIOR", font=("Arial", 25, "bold"), fg="black")
    etiqueta_nombre.config(text=f"Nombre: {visita['nombre_visita_historica']}")
    etiqueta_apellido.config(text=f"Apellido: {visita['apellido_visita_historica']}")
    etiqueta_depto.config(text=f"Nro depto: {visita['no_depto_visita_historica']}")
    etiqueta_patente.config(text=f"Patente: {visita['patente_visita_historica']}")
    
    # Rellenar el formulario automáticamente con los datos de la visita histórica
    input_rut_visita.delete(0, tk.END)
    input_rut_visita.insert(0, visita['rut_visita_historica'])

    input_dv_visita.delete(0, tk.END)
    input_dv_visita.insert(0, visita['dv_visita_historica'].upper())

    input_nombre_visita.delete(0, tk.END)
    input_nombre_visita.insert(0, visita['nombre_visita_historica'])

    input_apellido_visita.delete(0, tk.END)
    input_apellido_visita.insert(0, visita['apellido_visita_historica'])

    input_no_depto_dueno.delete(0, tk.END)
    input_no_depto_dueno.insert(0, visita['no_depto_visita_historica'])

    input_patente_visita.delete(0, tk.END)
    input_patente_visita.insert(0, visita['patente_visita_historica'])

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
    #este codigo le da la ubicacion al boton volver no tocar 
    boton_volver.place(relx=0.5, rely=0.82)

    # Limpiar los campos del formulario para registrar una nueva visita
    input_rut_visita.delete(0, tk.END)
    input_dv_visita.delete(0, tk.END)
    input_nombre_visita.delete(0, tk.END)
    input_apellido_visita.delete(0, tk.END)
    input_no_depto_dueno.delete(0, tk.END)
    input_patente_visita.delete(0, tk.END)
    combo_estacionamiento.set("Seleccionar")

    # Después de la función 'volver'
    def mostrar_boton_registrar_visita():
        """Mostrar el botón de Registrar Visita en la ventana principal."""
        boton_registrar_visita.place(relx=0.10, rely=0.77)

# Función para registrar la visita, al final de 'guardar_visita()' incluir:
    mostrar_boton_registrar_visita()


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
def preprocesar_imagen(imagen):
    """Aplica binarización, suavizado y escalado a la imagen para mejorar la detección OCR."""
    # Convertir la imagen a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    # Binarización de la imagen utilizando el método de umbralización de Otsu
    _, binarizada = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Suavizado para reducir el ruido (usamos el filtro GaussianBlur)
    suavizada = cv2.GaussianBlur(binarizada, (5, 5), 0)
    
    # Escalado de la imagen para mejorar la precisión de OCR (duplicamos el tamaño)
    escalada = cv2.resize(suavizada, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    return escalada
def mostrar_video():
    global n_frame, resultados, cap

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
            recorte_patente_preprocesada = preprocesar_imagen(recorte_patente)
            texto_patente = pytesseract.image_to_string(recorte_patente_preprocesada, config='--psm 8 --oem 3').strip()
            texto_patente = ''.join(filter(str.isalnum, texto_patente))
            texto_patente = validar_formato_patente(texto_patente)

            if texto_patente:
                # Consultar si la patente corresponde a una visita histórica
                visita_historica = consultar_visita_historica(texto_patente)
                if visita_historica:
                    # Mostrar datos de la visita histórica
                    mostrar_datos_visita_historica(visita_historica)

                    # Rodear la patente con un recuadro morado y agregar el texto de la visita histórica con la fecha de la última visita
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (128, 0, 128), 2)
                    cv2.putText(
                        frame,
                        f"Visita Anterior: {texto_patente}, Fecha: {visita_historica['momento_ingreso_historico'].strftime('%d-%m-%Y %H:%M:%S')}",
                        (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (128, 0, 128),
                        2
                    )
                else:
                    # Aquí está el código para manejar residentes o visitas actuales.
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

    # Mostrar nuevamente el botón de registrar visita
def mostrar_boton_registrar_visita():
        """Mostrar el botón de Registrar Visita en la ventana principal."""
        boton_registrar_visita.place(relx=0.10, rely=0.77)

def restablecer_visualizacion():
    """
    Restablece la interfaz a su estado inicial de 'SIN DETECCIONES'.
    """
    etiqueta_estado.config(text="SIN DETECCIONES", font=("Arial", 24, "bold"), fg="#696969")
    etiqueta_nombre.config(text="")
    etiqueta_apellido.config(text="")
    etiqueta_depto.config(text="")
    etiqueta_telefono.config(text="")
    etiqueta_patente.config(text="")
    etiqueta_fecha.config(text="")

def actualizar_estacionamientos_disponibles():
    """
    Consulta la base de datos para verificar qué estacionamientos están libres
    y actualiza el ComboBox para mostrar solo esos estacionamientos.
    """
    try:
        # Consultar los estacionamientos disponibles
        query = "SELECT numero_estacionamiento FROM estacionamiento WHERE estado = 'libre'"
        cursor_db.execute(query)
        estacionamientos_disponibles = [str(est[0]) for est in cursor_db.fetchall()]

        # Actualizar el ComboBox con los estacionamientos disponibles
        combo_estacionamiento['values'] = estacionamientos_disponibles

        # Si no hay estacionamientos disponibles, mostrar mensaje
        if not estacionamientos_disponibles:
            messagebox.showwarning("Estacionamientos Ocupados", "No hay estacionamientos disponibles en este momento.")

        # Establecer un valor predeterminado si hay opciones disponibles
        if estacionamientos_disponibles:
            combo_estacionamiento.set("Seleccionar")
        else:
            combo_estacionamiento.set("No disponible")

    except psycopg2.DatabaseError as e:
        print("Error al consultar los estacionamientos disponibles:", e)


def mostrar_formulario_visita():
    # Ocultar el frame de datos del residente
    frame_datos.place_forget()

    # Actualizar el ComboBox para mostrar solo los estacionamientos disponibles
    actualizar_estacionamientos_disponibles()

    # Mostrar los campos del formulario para registrar la visita en el espacio del frame de datos
    frame_formulario_visita.place(relx=0.05, rely=0.15, relwidth=0.3, relheight=0.70)

    boton_registrar_visita.place_forget()

    # Mostrar el botón "Volver" para cerrar el formulario de visita
    boton_volver.place(relx=0.5, rely=0.82)

def guardar_visita():
    rut_visita = input_rut_visita.get()
    dv_visita = input_dv_visita.get().upper()
    nombre_visita = input_nombre_visita.get()
    apellido_visita = input_apellido_visita.get()
    no_depto_dueno = input_no_depto_dueno.get()
    patente_visita = input_patente_visita.get().upper()
    estacionamiento_designado = combo_estacionamiento.get()  # Obtener el valor seleccionado del ComboBox
    momento_ingreso = datetime.now(timezone.utc)  # Almacenar la hora actual con zona horaria para evitar problemas de tipo de datetime

    # Validaciones
    if not re.fullmatch(r'[A-Z]{4}\d{2}', patente_visita):
        messagebox.showerror("Error de Validación", "El formato de la patente es incorrecto. Deben ser 4 letras seguidas de 2 números.")
        return

    if not re.fullmatch(r'\d{7,8}', rut_visita):
        messagebox.showerror("Error de Validación", "El RUT debe tener entre 7 y 8 dígitos, sin puntos ni guiones.")
        return

    if not re.fullmatch(r'[0-9K]', dv_visita):
        messagebox.showerror("Error de Validación", "El dígito verificador debe ser un número del 0 al 9 o la letra K.")
        return

    if not nombre_visita.istitle():
        messagebox.showerror("Error de Validación", "El nombre debe comenzar con mayúscula.")
        return

    if not apellido_visita.istitle():
        messagebox.showerror("Error de Validación", "El apellido debe comenzar con mayúscula.")
        return

    if not re.fullmatch(r'\d{1,3}', no_depto_dueno):
        messagebox.showerror("Error de Validación", "El número de departamento debe ser numérico y tener entre 1 y 3 dígitos.")
        return

    if estacionamiento_designado not in ["1", "2", "3"]:
        messagebox.showerror("Error de Validación", "Debe seleccionar un estacionamiento válido.")
        return

    try:
        # Consultar el rut_residente basado en el número de departamento
        query = "SELECT rut_residente FROM residente WHERE no_depto_residente = %s"
        cursor_db.execute(query, (no_depto_dueno,))
        resultado = cursor_db.fetchone()

        if not resultado:
            messagebox.showwarning("Depto no encontrado", f"No se encontró un residente asociado al departamento {no_depto_dueno}.")
            return

        residente_rut_residente = resultado[0]

        # Verificar si la visita es una visita histórica y generar un nuevo RUT si es necesario
        query_historico = "SELECT COUNT(*) FROM visita WHERE rut_visita = %s"
        cursor_db.execute(query_historico, (rut_visita,))
        count = cursor_db.fetchone()[0]

        if count > 0:
            # Generar un nuevo RUT si el RUT ya existe (para evitar la clave duplicada)
            rut_visita = str(random.randint(21000000, 21999999))
            dv_visita = calcular_dv(rut_visita)  # Puedes tener una función para calcular el DV

        #Insertar el registro de la visita en la base de datos
        query = """
        INSERT INTO visita (rut_visita, dv_visita, nombre_visita, apellido_visita, no_depto_dueno, momento_ingreso, momento_salida, patente_visita, residente_rut_residente, estacionamiento_designado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor_db.execute(query, (rut_visita, dv_visita, nombre_visita, apellido_visita, no_depto_dueno, momento_ingreso, None, patente_visita, residente_rut_residente, estacionamiento_designado))

        # Actualizar el estado del estacionamiento a 'ocupado' y establecer el momento de ingreso
        query_update_estacionamiento = "UPDATE estacionamiento SET estado = 'ocupado', id_visita = %s, momento_ingreso = %s WHERE numero_estacionamiento = %s"
        cursor_db.execute(query_update_estacionamiento, (rut_visita, momento_ingreso, estacionamiento_designado))

        # Verificar si la visita ya existe en el histórico y si no, insertarla
        query_check_historico = "SELECT COUNT(*) FROM visita_historico WHERE rut_visita_historica = %s AND patente_visita_historica = %s"
        cursor_db.execute(query_check_historico, (rut_visita, patente_visita))
        historico_count = cursor_db.fetchone()[0]

        if historico_count == 0:
            # Insertar el registro en la tabla visita_historico
            query_insert_historico = """
            INSERT INTO visita_historico (rut_visita_historica, dv_visita_historica, nombre_visita_historica, apellido_visita_historica, no_depto_visita_historica, patente_visita_historica, momento_ingreso_historico, momento_salida_historico, visita_rut_visita, multado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor_db.execute(query_insert_historico, (rut_visita, dv_visita, nombre_visita, apellido_visita, no_depto_dueno, patente_visita, momento_ingreso, None, rut_visita, False))

        conexion_db.commit()
        print(f"Visita registrada: {nombre_visita} {apellido_visita}")

        # Ocultar el formulario de visita y volver a mostrar el frame de datos del residente
        frame_formulario_visita.place_forget()
        frame_datos.place(relx=0.05, rely=0.15, relwidth=0.25, relheight=0.5)

        # Restablecer la visualización a su estado inicial
        restablecer_visualizacion()

        # Actualizar la interfaz de estacionamientos después de guardar la visita
        actualizar_estacionamientos()

        # Limpiar los campos del formulario
        limpiar_campos_formulario_visita()

        # Programar la alerta para 1 minuto después del registro de la visita (60,000 ms)
        alerta_un_minuto = ventana.after(60000, mostrar_alerta_un_minuto, nombre_visita, no_depto_dueno, estacionamiento_designado)

        # Guardar la referencia a la alerta programada
        alertas_programadas[estacionamiento_designado] = {
            'un_minuto': alerta_un_minuto,
            'dos_minutos': None  # Si también tienes una alerta para los dos minutos, puedes guardarla aquí luego
        }

    except psycopg2.DatabaseError as e:
        print("Error al guardar la visita:", e)
        conexion_db.rollback()

    # Mostrar nuevamente el botón de registrar visita
    mostrar_boton_registrar_visita()

def calcular_dv(rut):
    """
    Calcula el dígito verificador (DV) de un RUT chileno.
    """
    rut = list(map(int, reversed(rut)))
    factors = [2, 3, 4, 5, 6, 7]
    s = sum([digit * factors[i % len(factors)] for i, digit in enumerate(rut)])
    remainder = 11 - (s % 11)
    if remainder == 11:
        return '0'
    elif remainder == 10:
        return 'K'
    else:
        return str(remainder)
    
def limpiar_campos_formulario_visita():
    """
    Limpia todos los campos del formulario de visita para dejarlos vacíos.
    """
    input_rut_visita.delete(0, tk.END)
    input_dv_visita.delete(0, tk.END)
    input_nombre_visita.delete(0, tk.END)
    input_apellido_visita.delete(0, tk.END)
    input_no_depto_dueno.delete(0, tk.END)
    input_patente_visita.delete(0, tk.END)
    combo_estacionamiento.set("Seleccionar")


def enviar_alerta(nombre_visita, no_depto_dueno, estacionamiento_designado):
    """
    Muestra una alerta un minuto después de registrar la visita.
    """
    messagebox.showwarning(
        "Alerta de Tiempo",
        f"A la visita '{nombre_visita}' del departamento '{no_depto_dueno}' ubicada en el estacionamiento '{estacionamiento_designado}', le queda un minuto para retirarse."
    )

def enviar_alerta_multa(nombre_visita, no_depto_dueno, estacionamiento_designado):
    """
    Muestra una alerta dos minutos después de registrar la visita para advertir sobre una posible multa.
    """
    messagebox.showwarning(
        "Alerta de Multa",
        f"Notificar al residente que si no retira el vehículo en 5 minutos se le cursará una multa equivalente a 1 UTM.\n"
        f"Visita: '{nombre_visita}' del departamento '{no_depto_dueno}' ubicada en el estacionamiento '{estacionamiento_designado}'."
    )

def calcular_dv(rut):
    """
    Calcula el dígito verificador (DV) de un RUT chileno.
    """
    rut = list(map(int, reversed(rut)))
    factors = [2, 3, 4, 5, 6, 7]
    s = sum([digit * factors[i % len(factors)] for i, digit in enumerate(rut)])
    remainder = 11 - (s % 11)
    if remainder == 11:
        return '0'
    elif remainder == 10:
        return 'K'
    else:
        return str(remainder)

# Diccionario para registrar las alertas ya emitidas
alertas_emitidas = {
    1: False,
    2: False,
    3: False
}

def actualizar_estacionamientos():
    try:
        # Consultar el estado de los estacionamientos y las visitas asignadas
        query = """
        SELECT numero_estacionamiento, estado, momento_ingreso, id_visita
        FROM estacionamiento
        """
        cursor_db.execute(query)
        estacionamientos = cursor_db.fetchall()

        # Actualizar las etiquetas de estacionamiento en la interfaz
        for i in range(3):  # Asumimos que hay 3 estacionamientos
            estacionamiento_numero = i + 1
            estacionamiento = next((e for e in estacionamientos if e[0] == estacionamiento_numero), None)

            if estacionamiento:
                numero, estado, momento_ingreso, id_visita = estacionamiento
                label_estado = estacionamientos_frames[i]["estado"]
                label_tiempo = estacionamientos_frames[i]["tiempo"]

                if estado == 'ocupado' and momento_ingreso:
                    # Calcular el tiempo transcurrido
                    momento_ingreso = momento_ingreso.replace(tzinfo=None)  # Asegurarnos de que sea naive
                    tiempo_transcurrido = datetime.now() - momento_ingreso

                    # Calcular el tiempo restante (2 minutos = 120 segundos)
                    tiempo_restante = max(0, 120 - tiempo_transcurrido.total_seconds())
                    minutos, segundos = divmod(int(tiempo_restante), 60)

                    if tiempo_restante > 0:
                        label_estado.config(text="Ocupado", bg="red")
                        label_tiempo.config(text=f"Tiempo restante: {minutos}:{segundos:02d}")

                    else:
                        # Cambiar el mensaje a Tiempo Excedido si el tiempo restante es cero
                        tiempo_excedido = tiempo_transcurrido.total_seconds() - 120
                        minutos_excedidos, segundos_excedidos = divmod(int(tiempo_excedido), 60)
                        label_estado.config(text="Ocupado", bg="red")
                        label_tiempo.config(text=f"Tiempo Excedido: {minutos_excedidos}:{segundos_excedidos:02d}")

                else:
                    # Reiniciar la configuración del estacionamiento cuando esté libre
                    label_estado.config(text="Libre", bg="lightgreen")
                    label_tiempo.config(text="")
                    alertas_emitidas[estacionamiento_numero] = False

            else:
                # Si el estacionamiento no está asignado, se considera libre
                estacionamientos_frames[i]["estado"].config(
                    text="Libre",
                    bg="lightgreen"
                )
                estacionamientos_frames[i]["tiempo"].config(text="")
                alertas_emitidas[estacionamiento_numero] = False

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

etiqueta_fecha = tk.Label(frame_datos, text="", font=("Arial", 14), bg="white", fg="#4B0082")
etiqueta_fecha.pack(pady=5, anchor="w", padx=10)

etiqueta_rut = tk.Label(frame_datos, text="", font=("Arial", 14), bg="white", fg="#4B0082")
etiqueta_rut.pack(pady=5, anchor="w", padx=10)
# Crear el frame para el formulario de visita (oculto inicialmente)
# frame_formulario_visita = tk.Frame(ventana, bg="gray83", relief="solid", bd=2)

# etiqueta_formulario_patente = tk.Label(frame_formulario_visita, text="Patente Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
# etiqueta_formulario_patente.pack(pady=5, anchor="w", padx=10)

# input_patente_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
# input_patente_visita.pack(pady=10, anchor="w", padx=10)

# etiqueta_formulario_rut = tk.Label(frame_formulario_visita, text="RUT Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
# etiqueta_formulario_rut.pack(pady=5, anchor="w", padx=10)

# input_rut_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
# input_rut_visita.pack(pady=5, anchor="w", padx=10)

# etiqueta_formulario_dv = tk.Label(frame_formulario_visita, text="Dígito Verificador Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
# etiqueta_formulario_dv.pack(pady=5, anchor="w", padx=10)

# input_dv_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
# input_dv_visita.pack(pady=5, anchor="w", padx=10)

# etiqueta_formulario_nombre = tk.Label(frame_formulario_visita, text="Nombre Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
# etiqueta_formulario_nombre.pack(pady=5, anchor="w", padx=10)

# input_nombre_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
# input_nombre_visita.pack(pady=5, anchor="w", padx=10)

# etiqueta_formulario_apellido = tk.Label(frame_formulario_visita, text="Apellido Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
# etiqueta_formulario_apellido.pack(pady=5, anchor="w", padx=10)

# input_apellido_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
# input_apellido_visita.pack(pady=5, anchor="w", padx=10)

# etiqueta_formulario_no_depto = tk.Label(frame_formulario_visita, text="Nro Depto Residente: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
# etiqueta_formulario_no_depto.pack(pady=5, anchor="w", padx=10)

# etiqueta_rut_ = tk.Label(frame_formulario_visita, text="Nro Depto Residente: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
# etiqueta_rut_.pack(pady=5, anchor="w", padx=10)

# input_no_depto_dueno = tk.Entry(frame_formulario_visita, font=("Arial", 14))
# input_no_depto_dueno.pack(pady=5, anchor="w", padx=10)

# boton_guardar_visita = tk.Button(frame_formulario_visita, text="Guardar Visita", command=guardar_visita, font=("Arial", 14), bg="green", fg="white", width=15, height=2)
# boton_guardar_visita.pack(pady=12)
# boton_guardar_visita.place(relx=0.08, rely=0.82)

# Crear el botón "Volver" que aparece cuando se está en el formulario de visita
# boton_volver = tk.Button(frame_formulario_visita, text="Volver", command=volver, font=("Arial", 14), bg="red", fg="white", width=15, height=2)
# boton_volver.place_forget()  # Se inicia oculto

# Botón para registrar visita fuera del frame de datos del residente
# Crear el botón "Registrar Visita" con CustomTkinter
boton_registrar_visita = ctk.CTkButton(
    ventana, 
    text="Registrar Visita", 
    command=mostrar_formulario_visita, 
    font=("Arial", 18),  # Fuente grande para texto visible
    corner_radius=12,   # Bordes redondeados para un diseño más moderno
    fg_color="#28a745", # Color de fondo verde (verde brillante)
    bg_color="#2897cb",
    text_color="white",   # Color de texto blanco
    hover_color="#218838", # Color verde más oscuro al pasar el mouse
    width=200,          # Establecer un ancho fijo
    height=60,          # Establecer una altura fija
    border_width=3,     # Definir grosor del borde
    border_color="#218838" # Color del borde verde oscuro
)
boton_registrar_visita.place(relx=0.10, rely=0.77)


# Crear un label para mostrar el video a la derecha, ajustado proporcionalmente
label_video = tk.Label(ventana)
label_video.place(relx=0.45, rely=0.1, relwidth=0.42, relheight=0.55)

# Crear los bloques de estacionamientos debajo de la cámara
estacionamientos_frame = tk.Frame(ventana, bg="#009cd8")
estacionamientos_frame.place(relx=0.45, rely=0.7, relwidth=0.42, relheight=0.15)


# # Crear el frame para el formulario de visita (oculto inicialmente)
# frame_formulario_visita = tk.Frame(ventana, bg="gray83", relief="solid", bd=2)

# # Etiqueta y campo para patente visita
# etiqueta_formulario_patente = tk.Label(frame_formulario_visita, text="Patente Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
# etiqueta_formulario_patente.grid(row=0, column=0, padx=10, pady=5, sticky="w")
# input_patente_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
# input_patente_visita.grid(row=0, column=1, padx=10, pady=5)

# # Etiqueta y campo para RUT visita
# etiqueta_formulario_rut = tk.Label(frame_formulario_visita, text="RUT Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
# etiqueta_formulario_rut.grid(row=1, column=0, padx=10, pady=5, sticky="w")
# input_rut_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
# input_rut_visita.grid(row=1, column=1, padx=10, pady=5)

# # Etiqueta y campo para dígito verificador
# etiqueta_formulario_dv = tk.Label(frame_formulario_visita, text="DV Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
# etiqueta_formulario_dv.grid(row=2, column=0, padx=10, pady=5, sticky="w")
# input_dv_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
# input_dv_visita.grid(row=2, column=1, padx=10, pady=5)

# # Etiqueta y campo para nombre visita
# etiqueta_formulario_nombre = tk.Label(frame_formulario_visita, text="Nombre Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
# etiqueta_formulario_nombre.grid(row=3, column=0, padx=10, pady=5, sticky="w")
# input_nombre_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
# input_nombre_visita.grid(row=3, column=1, padx=10, pady=5)

# # Etiqueta y campo para apellido visita
# etiqueta_formulario_apellido = tk.Label(frame_formulario_visita, text="Apellido Visita:", font=("Arial", 12), bg="gray83", fg="#4B0082")
# etiqueta_formulario_apellido.grid(row=4, column=0, padx=10, pady=5, sticky="w")
# input_apellido_visita = tk.Entry(frame_formulario_visita, font=("Arial", 12))
# input_apellido_visita.grid(row=4, column=1, padx=10, pady=5)

# # Etiqueta y campo para número de departamento
# etiqueta_formulario_no_depto = tk.Label(frame_formulario_visita, text="Nro Depto:", font=("Arial", 12), bg="gray83", fg="#4B0082")
# etiqueta_formulario_no_depto.grid(row=5, column=0, padx=10, pady=5, sticky="w")
# input_no_depto_dueno = tk.Entry(frame_formulario_visita, font=("Arial", 12))
# input_no_depto_dueno.grid(row=5, column=1, padx=10, pady=5)

# # Combobox para seleccionar el estacionamiento
# etiqueta_estacionamiento = tk.Label(frame_formulario_visita, text="Estacionamiento:", font=("Arial", 12), bg="gray83", fg="#4B0082")
# etiqueta_estacionamiento.grid(row=6, column=0, padx=10, pady=5, sticky="w")

# # Crear un ComboBox con los estacionamientos disponibles
# estacionamientos_disponibles = ["1", "2", "3"]
# combo_estacionamiento = ttk.Combobox(frame_formulario_visita, values=estacionamientos_disponibles, font=("Arial", 12))
# combo_estacionamiento.grid(row=6, column=1, padx=10, pady=5)
# combo_estacionamiento.set("Seleccionar")  # Establecer un valor predeterminado
# Crear el frame para el formulario de visita
frame_formulario_visita = ctk.CTkFrame(ventana, fg_color="#fff59d", border_width=2, border_color="#4B0082")
frame_formulario_visita.pack(padx=20, pady=20, fill="both", expand=True)

# Título del formulario
titulo_formulario = ctk.CTkLabel(frame_formulario_visita, text="Formulario Agregar Visita", font=("Arial", 20, "bold"), text_color="#4B0082")
titulo_formulario.grid(row=0, column=0, columnspan=2, pady=10)

# Etiqueta y campo para patente visita
etiqueta_formulario_patente = ctk.CTkLabel(frame_formulario_visita, text="Patente Visita:", font=("Arial", 16), text_color="#4B0082")
etiqueta_formulario_patente.grid(row=1, column=0, padx=10, pady=10, sticky="w")
input_patente_visita = ctk.CTkEntry(frame_formulario_visita, font=("Arial", 16), width=300)  # Aumentamos el tamaño de la caja de texto
input_patente_visita.grid(row=1, column=1, padx=10, pady=10)

# Etiqueta y campo para RUT visita
etiqueta_formulario_rut = ctk.CTkLabel(frame_formulario_visita, text="RUT Visita:", font=("Arial", 16), text_color="#4B0082")
etiqueta_formulario_rut.grid(row=2, column=0, padx=10, pady=10, sticky="w")
input_rut_visita = ctk.CTkEntry(frame_formulario_visita, font=("Arial", 16), width=300)
input_rut_visita.grid(row=2, column=1, padx=10, pady=10)

# Etiqueta y campo para dígito verificador
etiqueta_formulario_dv = ctk.CTkLabel(frame_formulario_visita, text="DV Visita:", font=("Arial", 16), text_color="#4B0082")
etiqueta_formulario_dv.grid(row=3, column=0, padx=10, pady=10, sticky="w")
input_dv_visita = ctk.CTkEntry(frame_formulario_visita, font=("Arial", 16), width=300)
input_dv_visita.grid(row=3, column=1, padx=10, pady=10)

# Etiqueta y campo para nombre visita
etiqueta_formulario_nombre = ctk.CTkLabel(frame_formulario_visita, text="Nombre Visita:", font=("Arial", 16), text_color="#4B0082")
etiqueta_formulario_nombre.grid(row=4, column=0, padx=10, pady=10, sticky="w")
input_nombre_visita = ctk.CTkEntry(frame_formulario_visita, font=("Arial", 16), width=300)
input_nombre_visita.grid(row=4, column=1, padx=10, pady=10)

# Etiqueta y campo para apellido visita
etiqueta_formulario_apellido = ctk.CTkLabel(frame_formulario_visita, text="Apellido Visita:", font=("Arial", 16), text_color="#4B0082")
etiqueta_formulario_apellido.grid(row=5, column=0, padx=10, pady=10, sticky="w")
input_apellido_visita = ctk.CTkEntry(frame_formulario_visita, font=("Arial", 16), width=300)
input_apellido_visita.grid(row=5, column=1, padx=10, pady=10)

# Etiqueta y campo para número de departamento
etiqueta_formulario_no_depto = ctk.CTkLabel(frame_formulario_visita, text="Nro Depto:", font=("Arial", 16), text_color="#4B0082")
etiqueta_formulario_no_depto.grid(row=6, column=0, padx=10, pady=10, sticky="w")
input_no_depto_dueno = ctk.CTkEntry(frame_formulario_visita, font=("Arial", 16), width=300)
input_no_depto_dueno.grid(row=6, column=1, padx=10, pady=10)

# Etiqueta y campo para estacionamiento
etiqueta_estacionamiento = ctk.CTkLabel(frame_formulario_visita, text="Estacionamiento:", font=("Arial", 16), text_color="#4B0082")
etiqueta_estacionamiento.grid(row=7, column=0, padx=10, pady=10, sticky="w")

# Crear un ComboBox con los estacionamientos disponibles
estacionamientos_disponibles = ["1", "2", "3"]
combo_estacionamiento = ctk.CTkComboBox(frame_formulario_visita, values=estacionamientos_disponibles, font=("Arial", 16), width=300)
combo_estacionamiento.grid(row=7, column=1, padx=10, pady=10)
combo_estacionamiento.set("Seleccionar")  # Establecer un valor predeterminado
# Botón para guardar la visita
# Crear el botón "Guardar Visita" con CustomTkinter
boton_guardar_visita = ctk.CTkButton(
    frame_formulario_visita, 
    text="Guardar Visita", 
    command=guardar_visita, 
    font=("Arial", 14),  # Fuente un poco más grande
    corner_radius=10,   # Bordes redondeados
    fg_color="#28a745", # Color verde para el fondo (verde brillante)
    text_color="white",   # Color de texto blanco
    hover_color="#218838", # Color verde más oscuro al pasar el mouse
    width=200,          # Establecer un ancho fijo
    height=60,          # Establecer una altura fija
    border_width=3,     # Definir grosor del borde
    border_color="green" # Color verde para el borde
)

boton_volver_atras = ctk.CTkButton(
    frame_formulario_visita, 
    text="Volver", 
    command=volver, 
    font=("Arial", 14),  # Fuente un poco más grande
    corner_radius=10,   # Bordes redondeados
    fg_color="#dc3545", # Color verde para el fondo (verde brillante)
    text_color="white",   # Color de texto blanco
    hover_color="#c82333", # Color verde más oscuro al pasar el mouse
    width=200,          # Establecer un ancho fijo
    height=60,          # Establecer una altura fija
    border_width=3,     # Definir grosor del borde
    border_color="#c82333" # Color verde para el borde
)
boton_guardar_visita.grid(row=9, column=0, columnspan=2, pady=15)
boton_volver_atras.grid(row=10, column=0, columnspan=2, pady=15)



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

def mostrar_alerta_un_minuto(nombre_visita, no_depto_dueno, numero_estacionamiento):
    try:
        # Consultar el estado del estacionamiento para asegurarse de que sigue ocupado
        query = "SELECT estado FROM estacionamiento WHERE numero_estacionamiento = %s"
        cursor_db.execute(query, (numero_estacionamiento,))
        estado = cursor_db.fetchone()

        # Verificar si el estacionamiento sigue ocupado antes de mostrar la alerta
        if estado and estado[0] == 'ocupado':
            messagebox.showwarning("Alerta de Tiempo", f"A la visita '{nombre_visita}' del departamento '{no_depto_dueno}' ubicada en el estacionamiento '{numero_estacionamiento}', le queda un minuto para retirarse.")
    except psycopg2.DatabaseError as e:
        print("Error al consultar el estado del estacionamiento para la alerta:", e)




# Diccionario para almacenar las referencias de las alertas programadas por estacionamiento
alertas_programadas = {}

def liberar_estacionamiento_manual(numero_estacionamiento):
    try:
        # Obtener el momento de salida
        momento_salida = datetime.now(timezone.utc)

        # Actualizar el estado del estacionamiento en la base de datos y registrar el momento de salida
        query_update_estacionamiento = """
        UPDATE estacionamiento
        SET estado = 'libre', id_visita = NULL, momento_ingreso = NULL
        WHERE numero_estacionamiento = %s
        """
        cursor_db.execute(query_update_estacionamiento, (numero_estacionamiento,))

        # Actualizar el momento de salida en la tabla de visitas
        query_update_visita = """
        UPDATE visita
        SET momento_salida = %s
        WHERE estacionamiento_designado = %s AND momento_salida IS NULL
        """
        cursor_db.execute(query_update_visita, (momento_salida, numero_estacionamiento))

        # Actualizar el momento de salida en la tabla de visitas históricas
        query_update_visita_historico = """
        UPDATE visita_historico
        SET momento_salida_historico = %s
        WHERE patente_visita_historica = (
            SELECT patente_visita FROM visita
            WHERE estacionamiento_designado = %s AND momento_salida = %s
        )
        """
        cursor_db.execute(query_update_visita_historico, (momento_salida, numero_estacionamiento, momento_salida))

        # Confirmar los cambios en la base de datos
        conexion_db.commit()

        # Cancelar alertas programadas si existen
        if numero_estacionamiento in alertas_programadas:
            if alertas_programadas[numero_estacionamiento]['un_minuto']:
                ventana.after_cancel(alertas_programadas[numero_estacionamiento]['un_minuto'])
            if alertas_programadas[numero_estacionamiento]['dos_minutos']:
                ventana.after_cancel(alertas_programadas[numero_estacionamiento]['dos_minutos'])

            # Eliminar la referencia de las alertas canceladas
            del alertas_programadas[numero_estacionamiento]

        # Actualizar la interfaz después de liberar el estacionamiento
        actualizar_estacionamientos()

        # Actualizar el ComboBox de estacionamientos disponibles en el formulario de registro
        actualizar_estacionamientos_disponibles()

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
boton_inicio_sesion = ctk.CTkButton(
    ventana, 
    text="Iniciar sesión", 
    command=ir_a_inicio_sesion, 
    font=("Arial", 20),  # Cambiar el tamaño de la fuente
    corner_radius=15,   # Hacer las esquinas más redondeadas
    fg_color="#007bff", # Color de fondo
    text_color="white",   # Color de texto blanco
    hover_color="#0056b3", # Color al pasar el mouse
    width=200,          # Establecer un ancho fijo
    height=60,          # Establecer una altura fija
    border_width=3,     # Definir grosor del borde
    border_color="blue" # Color del borde
)
boton_inicio_sesion.place(relx=0.05, rely=0.05)

# Iniciar la visualización del video
mostrar_video()

# Ejecutar la aplicación
ventana.mainloop()

# Cerrar la conexión a la base de datos
conexion_db.close()
