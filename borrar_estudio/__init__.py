import logging
import mysql.connector
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':

        # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
        idEstudio = req.params.get('idEstudio')
        if idEstudio is None: return func.HttpResponse('Error: Se requiere el id del estudio.', status_code=400)

        # Conexión a la base de datos
        cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
        cursor = cnx.cursor()

        try:
            # Verificar que el estudio exista y no sea del mismo usuario
            query = "DELETE FROM estudios WHERE id = %s"
            values = (idEstudio,)
            cursor.execute(query, values)
            cnx.commit()

        except Exception as e:
            cnx.rollback()
            return func.HttpResponse('Error al borrar: {}'.format(str(e)), status_code=500)
        
        finally:
            cursor.close()
            cnx.close()
        
        # Enviar la respuesta HTTP con el id
        return func.HttpResponse("Estudio con id: {}, Borrado".format(str(idEstudio)), status_code=200)
        