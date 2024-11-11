import csv
import pytesseract
import re
import os
import sys

def crear_csv(resultados, output_path):
    """
    Escribir los resultados en un archivo CSV.

    Args:
        resultados (dict): Diccionario que contiene los resultados.
        output_path (str): Ruta del archivo CSV de salida.
    """
    # Verificar si hay resultados para escribir
    if not resultados:
        print("No hay resultados para escribir en el CSV.")
        return
    
    # Abrir el archivo CSV en modo escritura
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            # Definir los encabezados del CSV
            encabezados = [
                'n_frame', 'auto_id', 'auto_bbox',
                'patente_bbox', 'texto', 'score', 'puntuacion_texto'
            ]
            # Crear el escritor de CSV
            escritor = csv.DictWriter(f, fieldnames=encabezados)
            
            # Escribir el encabezado en el CSV
            escritor.writeheader()
            print("Encabezados del CSV escritos correctamente.")

            # Iterar sobre los resultados y escribir cada fila en el CSV
            for n_frame, datos_frame in resultados.items():
                for auto_id, datos in datos_frame.items():
                    # Verificar si los datos contienen las claves necesarias
                    if 'auto' in datos and 'patente' in datos:
                        fila = {
                            'n_frame': n_frame,
                            'auto_id': auto_id,
                            'auto_bbox': '[{} {} {} {}]'.format(
                                datos['auto']['auto_bbox'][0],
                                datos['auto']['auto_bbox'][1],
                                datos['auto']['auto_bbox'][2],
                                datos['auto']['auto_bbox'][3]
                            ),
                            'patente_bbox': '[{} {} {} {}]'.format(
                                datos['patente']['patente_bbox'][0],
                                datos['patente']['patente_bbox'][1],
                                datos['patente']['patente_bbox'][2],
                                datos['patente']['patente_bbox'][3]
                            ),
                            'texto': datos['patente']['texto'],
                            'score': datos['patente']['score'],
                            'puntuacion_texto': datos['patente'].get('puntuacion_texto', None)
                        }
                        # Escribir la fila en el CSV
                        escritor.writerow(fila)
                        print(f"Fila escrita para el frame {n_frame}, vehículo ID: {auto_id}")
                    else:
                        print(f"Faltan datos en el frame {n_frame}, vehículo ID: {auto_id}")

            print(f"Escritura de resultados completada. Resultados guardados en {output_path}.")
    except Exception as e:
        print(f"Error al escribir el archivo CSV: {e}")

# Función para verificar el contenido del diccionario 'resultados'
def verificar_resultados(resultados):
    if not resultados:
        print("El diccionario 'resultados' está vacío.")
        return

    print("Contenido del diccionario 'resultados' antes de escribir en CSV:")
    for n_frame, frame_data in resultados.items():
        for auto_id, data in frame_data.items():
            print(f"Frame {n_frame} - Vehículo ID: {auto_id} - Datos: {data}")

def obtener_auto(patente, id_seguimiento):
    """
    Asignar la patente detectada a un vehículo usando la información de seguimiento.

    Args:
        patente (list): Lista que contiene las coordenadas de la patente detectada.
        id_seguimiento (numpy.ndarray): Array con la información de seguimiento de los vehículos.

    Returns:
        tuple: Coordenadas del vehículo y el id del vehículo asignado.
    """
    if len(patente) >= 5:
        px1, py1, px2, py2, pscore = patente[:5]
    else:
        print("Error: La lista de patente no tiene suficientes valores.")
        return [0, 0, 0, 0, -1]

    mejor_iou = 0
    mejor_auto = [-1, -1, -1, -1, -1]

    # Comparar cada vehículo con la patente detectada para encontrar la mejor coincidencia (IoU)
    for vehiculo in id_seguimiento:
        vx1, vy1, vx2, vy2, vid = vehiculo

        # Calcular el área de intersección
        inter_x1 = max(px1, vx1)
        inter_y1 = max(py1, vy1)
        inter_x2 = min(px2, vx2)
        inter_y2 = min(py2, vy2)
        inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

        # Calcular áreas de la patente y el vehículo
        area_patente = (px2 - px1) * (py2 - py1)
        area_vehiculo = (vx2 - vx1) * (vy2 - vy1)

        # Calcular la unión de las áreas
        union_area = area_patente + area_vehiculo - inter_area

        # Calcular el coeficiente IoU (Intersection over Union)
        iou = inter_area / union_area if union_area > 0 else 0

        # Buscar la mejor coincidencia
        if iou > mejor_iou:
            mejor_iou = iou
            mejor_auto = [vx1, vy1, vx2, vy2, vid]

    # Asignar el ID del vehículo si el IoU es mayor a 0.2
    if mejor_iou > 0.2:
        return mejor_auto
    else:
        return [0, 0, 0, 0, -1]  # No asignar vehículo si no hay buena coincidencia

def leer_patente(recorte_patente):
    """
    Leer y procesar la patente desde una imagen de recorte.

    Args:
        recorte_patente (numpy.ndarray): Imagen del recorte de la patente.

    Returns:
        tuple: Texto de la patente y puntuación de confianza.
    """
    try:
        texto_patente = pytesseract.image_to_string(recorte_patente, config='--psm 8')
        puntuacion_texto = 1  # Puedes implementar una lógica para calcular la puntuación

        # Filtrar caracteres extraños
        texto_patente = ''.join(filter(str.isalnum, texto_patente))

        return texto_patente, puntuacion_texto
    except Exception as e:
        print(f"Error leyendo la patente: {e}")
        return None, 0
    
#######################################################

# Inicio de sesion
from bd import conectar

def validar_login(rut_admin, contrasena_admin):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        # Consulta hacia la tabla del administrador
        query = "SELECT rut_admin FROM administrador WHERE rut_admin = %s AND contrasena_admin = %s"
        cursor.execute(query, (rut_admin, contrasena_admin))
        resultado = cursor.fetchone()
        conexion.close()
        
        # Verificamos si se encontró un resultado (es decir, un administrador válido)
        if resultado:
            return resultado[0]  # Retorna rut_admin si las credenciales son válidas
    return None  

