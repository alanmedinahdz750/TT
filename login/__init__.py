import mysql.connector
import json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
        datos = req.get_json()

        # Validar que todos los campos requeridos estén presentes en el JSON
        campos_requeridos = ['nombre', 'contrasena']

        for campo in campos_requeridos:
            if campo not in datos:
                return func.HttpResponse('Error: El campo {} es requerido.'.format(campo), status_code=400)

        # Conexión a la base de datos
        cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
        cursor = cnx.cursor()

        try:
            # 1. Consultar el id de usuario con nombre y contraseña proporcionados
            query = "SELECT id FROM usuarios WHERE nombre = %s AND contrasena = %s"
            values = (datos['nombre'], datos['contrasena'])

            cursor.execute(query, values)
            # 2. Verificar si se encontró un usuario con las credenciales proporcionadas
            usuario = cursor.fetchone()

            if usuario is None:
                query = "SELECT nombre FROM usuarios WHERE nombre = %s"
                values = (datos['nombre'],)

                cursor.execute(query, values)
                # Verificar si se encontró un nombre de usuario
                nombre = cursor.fetchone()
                if nombre is None:
                    return func.HttpResponse('Error: Usuario no encontrado.', status_code=400)
                else:
                    return func.HttpResponse('Error: Contraseña incorrecta.', status_code=400)

            id_usuario = usuario[0]
            cnx.commit()

        except Exception as e:
            cnx.rollback()
            return func.HttpResponse('Error al realizar la consulta: {}'.format(str(e)), status_code=500)
        
        finally:
            cursor.close()
            cnx.close()

        # Crear un diccionario con el ID del usuario encontrado
        id_return = {'id': id_usuario}
        
        # Convertir el diccionario a un JSON válido
        json_response = json.dumps(id_return)
        
        # Enviar la respuesta HTTP con el JSON
        return func.HttpResponse(json_response, status_code=200)

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)