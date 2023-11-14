import azure.functions as func
import requests
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Obtener el parámetro 'estudio' de la solicitud
    estudio = req.params.get('estudio')

    if not estudio:
        return func.HttpResponse("Por favor, proporciona un parámetro 'estudio'", status_code=400)

    # Construir la URL completa
    url_base = 'https://demo.orthanc-server.com/instances/'
    url_completa = f"{url_base}{estudio}/preview"

    try:
        # Realizar la solicitud a la URL final
        respuesta = requests.get(url_completa)

        # Verificar si la solicitud fue exitosa (código de estado 200)
        if respuesta.status_code == 200:
             # Obtener la descripción (puedes personalizar esto según tus necesidades)
            descripcion = f"Descripción para {estudio}"

            # Devolver la imagen, su id y la descripción en un formato JSON
            respuesta_json = {
                "imagen": respuesta.content.decode("latin-1"),  # Decodificar la imagen y convertirla a cadena
                "id": estudio,
                "descripcion": descripcion
            }

            # Convertir el diccionario a una cadena JSON
            respuesta_json_str = json.dumps(respuesta_json)

            # Devolver la cadena JSON y establecer el tipo de contenido en la respuesta HTTP
            return func.HttpResponse(respuesta_json_str, mimetype="application/json")
        else:
            return func.HttpResponse(f"Error al obtener la imagen. Código de estado: {respuesta.status_code}", status_code=500)

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)