import mysql.connector
import azure.functions as func
import requests
import json
import base64


def main(req: func.HttpRequest) -> func.HttpResponse:
    instancia = req.params.get('instancia')
    if not instancia: return func.HttpResponse('Error: Falto el parametro instancia.', status_code=400)

    # Creamos el cursor para la base de datos
    cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
    cursor = cnx.cursor()
    try:
        # Consultar los estudios existentes
        query = "SELECT instancia, BodyPartExamined, Modality FROM estudios_orthanc where instancia = %s"    
        values = (instancia,)
        cursor.execute(query, values)
            
        # Pasar los valores a json
        resultado = cursor.fetchone()
        cnx.commit()

        if resultado is None:
            return func.HttpResponse('Error: No hay instancias de Orthanc.', status_code=400)
        
        url_base = 'https://demo.orthanc-server.com/instances/'
        url_completa = f"{url_base}{resultado[0]}/preview"

        try:
            # Realizar la solicitud a la URL final
            respuesta = requests.get(url_completa)

            # Verificar si la solicitud fue exitosa (código de estado 200)
            if respuesta.status_code == 200:
                # Devolver la imagen, su id y la descripción en un formato JSON
                retorno = {
                    "id": resultado[0],
                    "imagen_base64": base64.b64encode(respuesta.content).decode('utf-8'),  # Decodificar la imagen y convertirla a cadena
                    "parte" : resultado[1],
                    "tipo": resultado[2]
                }
                
                # Devolver la cadena JSON y establecer el tipo de contenido en la respuesta HTTP
                return func.HttpResponse(json.dumps(retorno), mimetype="application/json")
            else:
                return func.HttpResponse("No se pudo descargar el estudio {resultado[0]} de Orthanc", status_code=500)
    
        except Exception as e:
            return func.HttpResponse("Error al descargar el estudio {resultado[0]} de Orthanc", status_code=500)
    except Exception as e:
        return func.HttpResponse('Error al realizar la consulta de las instancias de Orthanc: {}'.format(str(e)), status_code=500)
    finally:
        cursor.close()
        cnx.close()
        
