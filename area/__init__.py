import mysql.connector
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:

    try:
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  P O S T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if req.method == 'POST':
            # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
            datos = req.get_json()

            # Validar que todos los campos requeridos estén presentes en el JSON
            campos_requeridos = ['area']

            for campo in campos_requeridos:
                if campo not in datos: return func.HttpResponse('Error: El campo {} es requerido.'.format(campo), status_code=400)
            
            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()

            try:
                cArea = datos['area']

                query = "SELECT * FROM Areas WHERE area = %s"
                values = (cArea,)

                cursor.execute(query, values)
                
                # Verificar si se encontró un area igual
                id_verificacion = cursor.fetchone()
                if id_verificacion is None:

                    # Insertar un nuevo estudio en la base de datos
                    query = "INSERT INTO Areas (area) VALUES (%s)"
                    values = (datos['area'],)

                    cursor.execute(query, values)

                    try:
                        # Obtener el ID de la escuela recién insertada
                        id_insertado = cursor.lastrowid
                    except Exception as e:
                        cnx.rollback()
                        return func.HttpResponse('Error al realizar la consulta: {}'.format(str(e)), status_code=500)

                    cnx.commit()
                else:
                    return func.HttpResponse('Ya existe el area: {}'.format(cArea), status_code=500)


            except Exception as e:
                cnx.rollback()
                return func.HttpResponse('Error al realizar la inserción: {}'.format(str(e)), status_code=500)
            
            finally:
                cursor.close()
                cnx.close()

            # Crear un diccionario con el ID del estudio insertado
            id_return = {'idArea': id_insertado}
            
            # Convertir el diccionario a un JSON válido
            json_response = json.dumps(id_return)
            
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse(json_response, status_code=200)
        
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  G E T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        elif req.method == 'GET':
            # Verificamos que exista el id
            idArea = req.params.get('id')
            #if idArea is None: return func.HttpResponse('Error: Se requiere el id de area.', status_code=400)
            
            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()
            
            try:
                # Consultar los estudios existentes
                values = []
                query = "SELECT * FROM Areas"
                if idArea:
                    query += " WHERE id = %s"
                    values = (idArea,)

                cursor.execute(query, values)
            
                # Pasar los valores a json
                # columns = [column[0] for column in cursor.description]
                # result = dict(zip(columns, cursor.fetchone()))
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                if results is None:
                    return func.HttpResponse('Error: Area no encontrada.', status_code=400)

                cnx.commit()

            except Exception as e:
                return func.HttpResponse('Error al realizar la consulta: {}'.format(str(e)), status_code=500)
            
            finally:
                cursor.close()
                cnx.close()
            
            json_response = json.dumps(results)

            return func.HttpResponse(json_response, status_code=200)


    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  O T R O S  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        else: 
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse("Método no permitido", status_code=405)
        
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  fin  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)
