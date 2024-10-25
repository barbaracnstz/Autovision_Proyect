import tkinter as tk
from tkinter import messagebox
from ultralytics import YOLO
import cv2
from PIL import Image, ImageTk
import numpy as np
import pytesseract
import psycopg2
import re
from datetime import datetime
import threading

# Ruta de Tesseract en tu sistema
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Conexión a la base de datos PostgreSQL
conexion_db = psycopg2.connect(
    host="localhost",
    database="autovision",
    user="postgres",
    password="holanda123."
)
cursor_db = conexion_db.cursor()

# Modelo YOLO para detección de patentes
detector_patente = YOLO('best.pt')

# Validar formato de la patente chilena
def validar_formato_patente(patente):
    patente = patente.upper()    
    patron = re.compile(r'^[A-Z]{2}[A-Z0-9]{2}\d{2}$')
    if patron.match(patente):
        return patente
    return None

# Consultar si la patente es de un residente y devolver los datos del residente
def consultar_residente(patente):
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

# Mostrar datos del residente
def mostrar_datos_residente(residente):
    etiqueta_estado.config(text="RESIDENTE", font=("Arial", 36, "bold"))
    etiqueta_nombre.config(text=f"Nombre: {residente['nombre_residente']}")
    etiqueta_apellido.config(text=f"Apellido: {residente['apellido_residente']}")
    etiqueta_depto.config(text=f"Nro depto: {residente['no_depto_residente']}")
    etiqueta_telefono.config(text=f"Teléfono: {residente['telefono_residente']}")
    etiqueta_patente.config(text=f"Patente: {residente['patente_vehiculo']}")

# Ocultar datos del residente y mostrar "Visita"
def ocultar_datos_residente():
    etiqueta_estado.config(text="VISITA", font=("Arial", 36, "bold"))
    etiqueta_nombre.config(text="")
    etiqueta_apellido.config(text="")
    etiqueta_depto.config(text="")
    etiqueta_telefono.config(text="")
    etiqueta_patente.config(text="")

# Procesar los fotogramas de la cámara y mostrar en la interfaz
def procesar_video():
    cap = cv2.VideoCapture(0)  # Abrir cámara

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detección de patentes
        resultados = detector_patente(frame, imgsz=640)[0]
        if len(resultados.boxes) > 0:
            patente_detectada = False
            for patente in resultados.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = patente

                if score > 0.5:
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                    recorte_patente = frame[int(y1):int(y2), int(x1):int(x2), :]
                    recorte_patente_gris = cv2.cvtColor(recorte_patente, cv2.COLOR_BGR2GRAY)
                    texto_patente = pytesseract.image_to_string(recorte_patente_gris, config='--psm 8').strip()
                    texto_patente = ''.join(filter(str.isalnum, texto_patente))  # Filtrar caracteres no alfanuméricos
                    texto_patente = validar_formato_patente(texto_patente)

                    if texto_patente:
                        residente = consultar_residente(texto_patente)
                        if residente:
                            mostrar_datos_residente(residente)
                            patente_detectada = True
                            break

            if not patente_detectada:
                ocultar_datos_residente()
        else:
            # Si no se detecta ninguna patente en el fotograma
            ocultar_datos_residente()

        # Mostrar el frame en la ventana de Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        etiqueta_video.config(image=img_tk)
        etiqueta_video.image = img_tk
        ventana.update()


    cap.release()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Control de Acceso - Autovisión")

# Definir el tamaño a media pantalla
screen_width = ventana.winfo_screenwidth()
screen_height = ventana.winfo_screenheight()
window_width = screen_width // 2
window_height = screen_height // 2
ventana.geometry(f'{window_width}x{window_height}+{screen_width // 4}+{screen_height // 4}')

# Crear los colores de fondo (blanco arriba, azul abajo)
ventana.configure(bg="white")

# Crear la parte superior (blanca)
header_frame = tk.Frame(ventana, bg='white')
header_frame.pack(fill='both', expand=True)

# Parte inferior azul
frame_inferior = tk.Frame(ventana, bg="blue", height=200)
frame_inferior.pack(fill='both', expand=True)

# Crear frame para la información del residente/visita (parte superior izquierda)
datos_frame = tk.Frame(header_frame, bg="white")
datos_frame.pack(side="left", fill="both", padx=20, pady=20)

# Etiqueta de estado Residente/Visita
etiqueta_estado = tk.Label(datos_frame, text="Residente o Visita", font=("Arial", 36, "bold"), bg="white")
etiqueta_estado.pack(pady=10)

# Información del residente
etiqueta_nombre = tk.Label(datos_frame, text="", font=("Arial", 14), bg="white")
etiqueta_nombre.pack(anchor="w")

etiqueta_apellido = tk.Label(datos_frame, text="", font=("Arial", 14), bg="white")
etiqueta_apellido.pack(anchor="w")

etiqueta_depto = tk.Label(datos_frame, text="", font=("Arial", 14), bg="white")
etiqueta_depto.pack(anchor="w")

etiqueta_telefono = tk.Label(datos_frame, text="", font=("Arial", 14), bg="white")
etiqueta_telefono.pack(anchor="w")

etiqueta_patente = tk.Label(datos_frame, text="", font=("Arial", 14), bg="white")
etiqueta_patente.pack(anchor="w")

# Crear botón de agregar visita
boton_agregar_visita = tk.Button(frame_inferior, text="Agregar Visita", bg="yellow", font=("Arial", 12))
boton_agregar_visita.pack(pady=20, padx=20, side="left")

# Crear espacios para otros elementos (mockup con casillas vacías)
casilla_1 = tk.Label(frame_inferior, text="1", font=("Arial", 14), width=10, height=5, bg="white")
casilla_1.pack(side="left", padx=10)
casilla_2 = tk.Label(frame_inferior, text="2", font=("Arial", 14), width=10, height=5, bg="white")
casilla_2.pack(side="left", padx=10)
casilla_3 = tk.Label(frame_inferior, text="3", font=("Arial", 14), width=10, height=5, bg="white")
casilla_3.pack(side="left", padx=10)

# Crear etiqueta para mostrar el video en tiempo real (parte superior derecha)
etiqueta_video = tk.Label(header_frame)
etiqueta_video.pack(side="right", expand=True, fill="both", padx=20, pady=20)

# Hilo para procesar el video
hilo_video = threading.Thread(target=procesar_video, daemon=True)
hilo_video.start()

# Iniciar la ventana principal
ventana.mainloop()

# Cerrar la conexión a la base de datos
cursor_db.close()
conexion_db.close()
