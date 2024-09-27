# Importar las librerías
from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import *
from util import obtener_auto, leer_patente, crear_csv  # Asegúrate de que estas funciones estén correctamente definidas
import pytesseract
import re
from datetime import datetime
import psycopg2
from fuzzywuzzy import fuzz

# Ruta de Tesseract en tu sistema (ajustar según corresponda)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Conexión a la base de datos PostgreSQL
conexion_db = psycopg2.connect(
    host="localhost",
    database="control_car",
    user="postgres",
    password="holanda123."
)
cursor_db = conexion_db.cursor()

# Diccionario para almacenar resultados
resultados = {}

# Inicializar objeto de seguimiento con Sort
seguimiento_motos = Sort()

# Cargar Modelos YOLO
coco_model = YOLO('yolov8m.pt')  # Prueba con un modelo más grande para mejor precisión
detector_patente = YOLO('best.pt')  # Modelo para detección de patentes

# Capturar Video desde la Webcam o archivo de video
cap = cv2.VideoCapture('ejemplo.mp4')

# Definir clases de vehículos según COCO (puedes ajustar las clases según necesites)
autos = [2]  # Clases de vehículos en COCO: [Car, Motorcycle, Bus, Truck]

# Verificar si la cámara se ha abierto correctamente
if not cap.isOpened():
    print("Error al abrir la cámara.")
    exit()

n_frame = 0  # Contador de fotogramas
ret = True

# Inicializar id_seguimiento como una matriz vacía antes del bucle principal
id_seguimiento = np.empty((0, 5))  # El seguimiento inicial vacío

def validar_formato_patente(patente):
    """
    Valida el formato de la patente chilena: los primeros 2 caracteres son letras y los últimos 2 son números.
    """
    # Reemplazar caracteres que suelen confundirse
    patente = patente.upper()    
    # Expresión regular para el formato "AA-XX-11", donde XX puede ser letras o números
    patron = re.compile(r'^[A-Z]{2}[A-Z0-9]{2}\d{2}$')
    if patron.match(patente):
        return patente
    return None

def consultar_residente(patente):
    """
    Consulta si una patente pertenece a un residente en la base de datos.
    """
    cursor_db.execute("SELECT residente_rut FROM patente WHERE patente_vehiculo = %s", (patente,))
    resultado = cursor_db.fetchone()
    return resultado is not None

while ret:
    # Leer cada fotograma del video
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el fotograma.")
        break

    # Ajustar tamaño del fotograma (opcional: ajusta según tus necesidades)
    ancho_destino = 640  # Ancho deseado para la ventana
    alto_destino = int((ancho_destino / frame.shape[1]) * frame.shape[0])
    frame = cv2.resize(frame, (ancho_destino, alto_destino))

    # Incrementar el contador de fotogramas
    n_frame += 1
    resultados[n_frame] = {}

    # Detección de Vehículos
    detecciones = coco_model(frame)[0]
    detecciones_ = []
    for deteccion in detecciones.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = deteccion
        if int(class_id) in autos and score > 0.5:  # Ajusta el umbral de confianza si es necesario
            detecciones_.append([x1, y1, x2, y2, score])
            # Dibujar rectángulo alrededor del vehículo
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(frame, f'Vehiculo', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Verificar detecciones antes de pasar al seguimiento
    if len(detecciones_) == 0:
        print("No se detectaron vehículos en este fotograma.")
    else:
        print("Detecciones antes de seguimiento:", detecciones_)

    # Actualizar seguimiento solo si hay detecciones válidas
    if len(detecciones_) > 0:
        id_seguimiento = seguimiento_motos.update(np.asarray(detecciones_))
    else:
        # Si no hay detecciones, mantener id_seguimiento vacío para evitar errores
        id_seguimiento = np.empty((0, 5))  # Crear una matriz vacía con la misma estructura

    # Detección de Patentes
    detector_patentes = detector_patente(frame)[0]
    for patente in detector_patentes.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = patente

        if score > 0.5:  # Ajustar umbral de confianza para la detección de patentes
            # Dibujar rectángulo alrededor de la patente en rojo
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

            # Cortar Patente
            recorte_patente = frame[int(y1):int(y2), int(x1):int(x2), :]

            # Procesar la Patente (se eliminan filtros innecesarios)
            recorte_patente_gris = cv2.cvtColor(recorte_patente, cv2.COLOR_BGR2GRAY)
            # Eliminamos threshold para mejorar OCR

            # Leer Números de la Patente con OCR
            texto_patente = pytesseract.image_to_string(recorte_patente_gris, config='--psm 8').strip()
            texto_patente = ''.join(filter(str.isalnum, texto_patente))  # Filtrar caracteres no alfanuméricos

            # Validar formato de la patente
            texto_patente = validar_formato_patente(texto_patente)

            if texto_patente:
                # Cambiar el color a verde si es un residente
                if consultar_residente(texto_patente):
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f'Residente: {texto_patente}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    print(f"Patente residente detectada: {texto_patente}")
                else:
                    cv2.putText(frame, f'Visita: {texto_patente}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    print(f"Patente visita detectada: {texto_patente}")

                # Asignar Patente a un Vehículo
                if id_seguimiento.shape[0] > 0:
                    xauto1, yauto1, xauto2, yauto2, auto_id = obtener_auto(patente, id_seguimiento)
                    if auto_id != -1:
                        print(f"Patente asignada al vehículo con ID: {auto_id}")
                        resultados[n_frame][auto_id] = {
                            'auto': {
                                'auto_bbox': [xauto1, yauto1, xauto2, yauto2]
                            },
                            'patente': {
                                'patente_bbox': [x1, y1, x2, y2],
                                'texto': texto_patente,
                                'score': score
                            }
                        }
                        print(f"Resultados almacenados para el vehículo ID: {auto_id} en el frame {n_frame}")
                    else:
                        print("No se pudo asignar la patente a un vehículo en este fotograma.")
                else:
                    print("No hay vehículos para asignar la patente.")
            else:
                print("Formato de patente no válido.")

    # Mostrar la fecha y la hora en la esquina inferior derecha
    fecha_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    (alto_frame, ancho_frame) = frame.shape[:2]
    cv2.putText(frame, fecha_hora, (ancho_frame - 250, alto_frame - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Mostrar fotograma con anotaciones
    cv2.imshow("Deteccion de Vehiculos y Patentes", frame)
    if cv2.waitKey(1) == 27:  # Si se presiona ESC, salir del bucle
        break

# Mostrar el contenido del diccionario 'resultados' antes de escribir en CSV
print("Contenido del diccionario 'resultados' antes de escribir en CSV:")
for n_frame, frame_data in resultados.items():
    for auto_id, data in frame_data.items():
        print(f"Frame {n_frame} - Vehículo ID: {auto_id} - Datos: {data}")

# Guardar resultados en CSV
crear_csv(resultados, 'resultados_patentes.csv')
print("Resultados guardados en resultados_patentes.csv")

# Cerrar la conexión a la base de datos
cursor_db.close()
conexion_db.close()
print("Conexión a la base de datos cerrada.")

# Liberar la captura y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()

