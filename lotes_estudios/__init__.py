import mysql.connector
import azure.functions as func
import requests
import json
import base64

def main(req: func.HttpRequest) -> func.HttpResponse:
    limit = req.params.get('limit')
    if not limit: return func.HttpResponse('Error: Falto el parametro limit.', status_code=400)

    # Creamos el cursor para la base de datos
    cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
    cursor = cnx.cursor()
    try:
        # Consultar los estudios existentes
        query = "SELECT instancia, BodyPartExamined, Modality FROM estudios_orthanc ORDER BY RAND() LIMIT %s"    
        values = (int(limit),)
        cursor.execute(query, values)
            
        # Pasar los valores a json
        resultados = cursor.fetchall()

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
        retorno = {}
        i = 0

        for elemento in lista_instancias:
            i+=1
            url_base = 'https://demo.orthanc-server.com/instances/'
            url_completa = f"{url_base}{elemento['instancia']}/preview"

            try:
                # Realizar la solicitud a la URL final
                respuesta = requests.get(url_completa)

                # Verificar si la solicitud fue exitosa (código de estado 200)
                if respuesta.status_code == 200:
                    # Devolver la imagen, su id y la descripción en un formato JSON
                    retorno[elemento['instancia']] = {
                        "imagen_base64": base64.b64encode(respuesta.content).decode('utf-8'),  # Decodificar la imagen y convertirla a cadena
                        "parte" : elemento['BodyPartExamined'],
                        "tipo": elemento['Modality']
                    }
                else:
                    print("Error al descargar el estudio {i} de Orthanc")
    
            except Exception as e:
                print(f"Error al descargar el estudio {i} con id {elemento['instancia']}: {str(e)}")
                #return func.HttpResponse(f"Error al descargar el estudio {i} con id {elemento['instancia']}: {str(e)}", status_code=500)
        
        # Convertir el diccionario a una cadena JSON
        respuesta_json_str = json.dumps(retorno)

        # Devolver la cadena JSON y establecer el tipo de contenido en la respuesta HTTP
        return func.HttpResponse(respuesta_json_str, mimetype="application/json")
    
    except Exception as e:
        return func.HttpResponse('Error al realizar la consulta de las instancias de Orthanc: {}'.format(str(e)), status_code=500)
    finally:
        cursor.close()
        cnx.close()