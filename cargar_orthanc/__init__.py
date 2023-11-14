import mysql.connector
import json
import azure.functions as func

def insertar_datos_en_base_de_datos(datos):
    try:
        # Conexión a la base de datos
        cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
        cursor = cnx.cursor()

        try:
            for instancia, info in datos.items():
                # Insertar datos en la tabla estudios_orthanc
                query = "INSERT INTO estudios_orthanc (instancia, informacion, SeriesDescription, StudyDescription, BodyPartExamined, Modality) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (instancia, info['informacion'], info['SeriesDescription'], info['StudyDescription'], info['BodyPartExamined'], info['Modality'])

                cursor.execute(query, values)

            cnx.commit()
        except Exception as e:
            cnx.rollback()
            raise e
        finally:
            cursor.close()
            cnx.close()

    except Exception as e:
        raise e


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
        datos = req.get_json()

        # Validar que todos los campos requeridos estén presentes en el JSON
        campos_requeridos = ['instancia']

        '''for instancia, info in datos.items():
            for campo in campos_requeridos:
                if campo not in info:
                    return func.HttpResponse('Error: El campo {} es requerido para la instancia {}.'.format(campo, instancia), status_code=400)
        '''

        # Llamar a la función para insertar datos en la base de datos
        insertar_datos_en_base_de_datos(datos)

        # Enviar la respuesta HTTP
        return func.HttpResponse('Datos insertados correctamente en la base de datos.', status_code=200)

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)