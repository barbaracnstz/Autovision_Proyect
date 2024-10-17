import re
from datetime import datetime
from ultralytics import YOLO
import cv2
import numpy as np
import pytesseract
import psycopg2
from sort.sort import *
from util import obtener_auto, leer_patente, crear_csv
from fuzzywuzzy import fuzz
import tkinter as tk
from PIL import Image, ImageTk
import inicio_sesion  # Importa el archivo de inicio de sesión


# Ruta de Tesseract en tu sistema (ajustar según corresponda)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

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
coco_model = YOLO('yolov8m.pt')
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
    patron = re.compile(r'^[A-Z]{2}[A-Z0-9]{2}\d{2}$')
    return patente if patron.match(patente) else None

def consultar_residente(patente):
    """Consulta si una patente pertenece a un residente en la base de datos."""
    cursor_db.execute("SELECT residente_rut_residente FROM vehiculo WHERE patente_vehiculo = %s", (patente,))
    return cursor_db.fetchone() is not None

def mostrar_video():
    global n_frame, resultados

    # Leer cada fotograma del video
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el fotograma.")
        return

    n_frame += 1
    resultados[n_frame] = {}

    # Detección de Vehículos
    detecciones = coco_model(frame)[0]
    detecciones_ = []
    for deteccion in detecciones.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = deteccion
        if int(class_id) in [2, 3, 5, 7] and score > 0.5:  # Filtrar por clases
            detecciones_.append([x1, y1, x2, y2, score])
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)

    # Actualizar seguimiento solo si hay detecciones válidas
    id_seguimiento = seguimiento_motos.update(np.asarray(detecciones_)) if detecciones_ else np.empty((0, 5))

    # Detección de Patentes
    detector_patentes = detector_patente(frame)[0]
    for patente in detector_patentes.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = patente
        if score > 0.5:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
            recorte_patente = frame[int(y1):int(y2), int(x1):int(x2), :]
            recorte_patente_gris = cv2.cvtColor(recorte_patente, cv2.COLOR_BGR2GRAY)
            texto_patente = pytesseract.image_to_string(recorte_patente_gris, config='--psm 8').strip()
            texto_patente = ''.join(filter(str.isalnum, texto_patente))
            texto_patente = validar_formato_patente(texto_patente)

            if texto_patente:
                if consultar_residente(texto_patente):
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f'Residente: {texto_patente}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, f'Visita: {texto_patente}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Asignar Patente a un Vehículo
                if id_seguimiento.shape[0] > 0:
                    xauto1, yauto1, xauto2, yauto2, auto_id = obtener_auto(patente, id_seguimiento)
                    if auto_id != -1:
                        resultados[n_frame][auto_id] = {
                            'auto': {'auto_bbox': [xauto1, yauto1, xauto2, yauto2]},
                            'patente': {'patente_bbox': [x1, y1, x2, y2], 'texto': texto_patente, 'score': score}
                        }

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
fondo = Image.open("/Autovision_Proyect/Fondo2.png").resize((ventana.winfo_screenwidth(), ventana.winfo_screenheight()))
fondo_imagen = ImageTk.PhotoImage(fondo)

# Crear un canvas para el fondo
canvas = tk.Canvas(ventana, width=ventana.winfo_screenwidth(), height=ventana.winfo_screenheight())
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=fondo_imagen, anchor="nw")

# Añadir el botón "Iniciar sesión" en la esquina superior izquierda
boton_inicio_sesion = tk.Button(ventana, text="Iniciar sesión", command=ir_a_inicio_sesion, font=('Arial', 12), bg='yellow')
boton_inicio_sesion.place(x=10, y=10)  # Posiciona el botón en la esquina superior izquierda

# Label para mostrar el video
label_video = tk.Label(ventana)
label_video.place(relx=1, rely=0, anchor="ne")  # Posicionar en la esquina superior derecha

# Iniciar el video
mostrar_video()

# Iniciar el bucle de Tkinter
ventana.mainloop()

# Liberar la captura y cerrar las ventanas al final
cap.release()
cv2.destroyAllWindows()
cursor_db.close()
conexion_db.close()
print("Conexión a la base de datos cerrada.")
