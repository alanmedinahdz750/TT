import mysql.connector
import json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
        idUsuario = req.params.get('idUsuario')

        # Conexión a la base de datos
        cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
        cursor = cnx.cursor()

        try:
            # 1. Consultar el id de usuario con correo y contraseña proporcionados
            query = "SELECT * FROM usuarios WHERE id = %s"
            values = (idUsuario, )

            cursor.execute(query, values)
            # 2. Verificar si se encontró un usuario con las credenciales proporcionadas
            cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
            datosUsuario = cursor.fetchone()

            if datosUsuario is None:
                return func.HttpResponse('Error: Usuario no encontrado.', status_code=400)

            cnx.commit()

        except Exception as e:
            return func.HttpResponse('Error al realizar la consulta: {}'.format(str(e)), status_code=500)
        
        finally:
            cursor.close()
            cnx.close()
        
        # Convertir el diccionario a un JSON válido
        json_response = json.dumps(datosUsuario)
        
        # Enviar la respuesta HTTP con el JSON
        return func.HttpResponse(json_response, status_code=200)

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)