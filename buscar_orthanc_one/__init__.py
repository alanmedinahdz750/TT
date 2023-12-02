import mysql.connector
import azure.functions as func
import requests
import json
import base64

from concurrent.futures import ThreadPoolExecutor

def descargar_imagen(instancia, i, BodyPartExamined,Modality):
    url_base = 'https://demo.orthanc-server.com/instances/'
    url_completa = f"{url_base}{instancia}/preview"

    try:
        # Realizar la solicitud a la URL final
        respuesta = requests.get(url_completa)

        # Verificar si la solicitud fue exitosa (código de estado 200)
        if respuesta.status_code == 200:
            # Devolver la imagen, su id y la descripción en un formato JSON
            return {
                "id": instancia,
                "imagen_base64": base64.b64encode(respuesta.content).decode('utf-8'),  # Decodificar la imagen y convertirla a cadena
                "parte": BodyPartExamined,
                "tipo": Modality
            }
        else:
            print(f"Error al descargar el estudio {i} de Orthanc")

    except Exception as e:
        print(f"Error al descargar el estudio {i} con id {instancia}: {str(e)}")

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Obtener los valores de los parámetros
    param = req.params.get('param').upper()

    if not param: return func.HttpResponse("Se necesita el parametro 'param' para hacer la busqueda", status_code=500)

    # Creamos el cursor para la base de datos
    cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
    cursor = cnx.cursor()

    try:
        try:
            query = "SELECT instancia, BodyPartExamined, Modality FROM estudios_orthanc WHERE Modality LIKE %s OR StudyDescription LIKE %s OR BodyPartExamined LIKE %s OR SeriesDescription LIKE %s OR informacion LIKE %s LIMIT 15"

            cursor.execute(query, ('%' + param + '%', '%' + param + '%', '%' + param + '%', '%' + param + '%', '%' + param + '%')) 

            try: 
                # Pasar los valores a json
                resultados = cursor.fetchall()
            except Exception as e:
                # Hubo algun problema, el resultado es vacio:
                resultados = None
        except Exception as e:
            return func.HttpResponse('Error al realizar la consulta de las instancias en MySQL: {}'.format(str(e)), status_code=500)

        if resultados is None:
            return func.HttpResponse('Error: No hay instancias de Orthanc.', status_code=400)

        # Crear un array para almacenar las instancias
        lista_instancias = []

        # Recorrer los resultados
        for resultado in resultados:
            # Crear un diccionario con los datos de cada instancia
            instancia_info = {
                'instancia': resultado[0],
                'BodyPartExamined': resultado[1],
                'Modality': resultado[2]
            }
            lista_instancias.append(instancia_info)

        cnx.commit()
        # creamos el diccionario de retorno
        retorno = []

        with ThreadPoolExecutor() as executor:
            # Utilizar ThreadPoolExecutor para descargar imágenes en paralelo
            descargas = [executor.submit(descargar_imagen, instancia['instancia'], i + 1, instancia['BodyPartExamined'], instancia['Modality']) for i, instancia in enumerate(lista_instancias)]

            for descarga in descargas:
                resultado_descarga = descarga.result()
                if resultado_descarga:
                    retorno.append(resultado_descarga)

        # Convertir el diccionario a una cadena JSON
        respuesta_json_str = json.dumps(retorno)

        # Devolver la cadena JSON y establecer el tipo de contenido en la respuesta HTTP
        return func.HttpResponse(respuesta_json_str, mimetype="application/json")

    except Exception as e:
        return func.HttpResponse('Error al realizar la consulta de las instancias de Orthanc: {}'.format(str(e)), status_code=500)
    finally:
        cursor.close()
        cnx.close()
