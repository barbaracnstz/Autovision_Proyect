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

# Ruta de Tesseract en tu sistema (ajustar según corresponda)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Conexión a la base de datos PostgreSQL
conexion_db = psycopg2.connect(
    host="localhost",
    database="autovision",
    user="postgres",
    password="1234"
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
    frame_formulario_visita.place(relx=0.05, rely=0.15, relwidth=0.3, relheight=0.7)

def guardar_visita():
    rut_visita = input_rut_visita.get()
    dv_visita = input_dv_visita.get()
    nombre_visita = input_nombre_visita.get()
    apellido_visita = input_apellido_visita.get()
    no_depto_dueno = input_no_depto_dueno.get()
    patente_visita = input_patente_visita.get()
    estacionamiento_designado = input_estacionamiento_designado.get()
    momento_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    momento_salida = momento_ingreso  # Inicialmente la misma hora de ingreso
    residente_rut_residente = input_rut_residente.get()
    
    query = """
    INSERT INTO visita (rut_visita, dv_visita, nombre_visita, apellido_visita, no_depto_dueno, momento_ingreso, momento_salida, patente_visita, residente_rut_residente, estacionamiento_designado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor_db.execute(query, (rut_visita, dv_visita, nombre_visita, apellido_visita, no_depto_dueno, momento_ingreso, momento_salida, patente_visita, residente_rut_residente, estacionamiento_designado))
    conexion_db.commit()
    print(f"Visita registrada: {nombre_visita} {apellido_visita}")
    
    # Ocultar el formulario de visita y volver a mostrar el frame de datos del residente
    frame_formulario_visita.place_forget()
    frame_datos.place(relx=0.05, rely=0.15, relwidth=0.25, relheight=0.5)

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

etiqueta_formulario_no_depto = tk.Label(frame_formulario_visita, text="Nro Departamento Residente: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
etiqueta_formulario_no_depto.pack(pady=5, anchor="w", padx=10)

input_no_depto_dueno = tk.Entry(frame_formulario_visita, font=("Arial", 14))
input_no_depto_dueno.pack(pady=5, anchor="w", padx=10)

etiqueta_formulario_patente = tk.Label(frame_formulario_visita, text="Patente Visita: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
etiqueta_formulario_patente.pack(pady=5, anchor="w", padx=10)

input_patente_visita = tk.Entry(frame_formulario_visita, font=("Arial", 14))
input_patente_visita.pack(pady=10, anchor="w", padx=10)

etiqueta_formulario_rut_residente = tk.Label(frame_formulario_visita, text="RUT Residente: ", font=("Arial", 14), bg="gray83", fg="#4B0082")
etiqueta_formulario_rut_residente.pack(pady=5, anchor="w", padx=10)

input_rut_residente = tk.Entry(frame_formulario_visita, font=("Arial", 14))
input_rut_residente.pack(pady=10, anchor="w", padx=10)

boton_guardar_visita = tk.Button(frame_formulario_visita, text="Guardar Visita", command=guardar_visita, font=("Arial", 14), bg="green", fg="white")
boton_guardar_visita.pack(pady=12)

# Botón para registrar visita fuera del frame de datos del residente
boton_registrar_visita = tk.Button(ventana, text="Registrar Visita", command=mostrar_formulario_visita, font=("Arial", 18), bg="blue", fg="white", width=20, height=2)
boton_registrar_visita.place(relx=0.10, rely=0.77)

# Crear un label para mostrar el video a la derecha, ajustado proporcionalmente
label_video = tk.Label(ventana)
label_video.place(relx=0.45, rely=0.1, relwidth=0.42, relheight=0.55)

# Crear los bloques de estacionamientos debajo de la cámara
estacionamientos_frame = tk.Frame(ventana, bg="#009cd8")
estacionamientos_frame.place(relx=0.45, rely=0.7, relwidth=0.42, relheight=0.15)

for i in range(3):
    estacionamiento = tk.Label(estacionamientos_frame, text=f"Estacionamiento {i + 1}", font=("Arial", 16), bg="lightgray", relief="solid", width=15, height=2)
    estacionamiento.grid(row=0, column=i, padx=15, pady=10)

# Botón para ir al inicio de sesión en la parte superior izquierda
boton_inicio_sesion = tk.Button(ventana, text="Iniciar sesión", command=ir_a_inicio_sesion, font=("Arial", 16), bg="red", fg="white")
boton_inicio_sesion.place(relx=0.05, rely=0.05)

# Iniciar la visualización del video
mostrar_video()

# Ejecutar la aplicación
ventana.mainloop()

# Cerrar la conexión a la base de datos
conexion_db.close()
