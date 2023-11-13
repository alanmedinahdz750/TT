import azure.functions as func
import requests

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
            # Devolver la imagen y establecer el tipo de contenido en la respuesta HTTP
            return func.HttpResponse(respuesta.content, mimetype="image/png")
        else:
            return func.HttpResponse(f"Error al obtener la imagen. Código de estado: {respuesta.status_code}", status_code=500)

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)