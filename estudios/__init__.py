import mysql.connector
import json
import base64
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  P O S T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        if req.method == 'POST':
            # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
            datos = req.get_json()
            idUsuario = req.params.get('idUsuario')

            if idUsuario is None: return func.HttpResponse('Error: Se requiere el id del usuario.', status_code=400)

            # Validar que todos los campos requeridos estén presentes en el JSON
            campos_requeridos = ['imagen', 'json', 'descripcion', 'tipo', 'parte_cuerpo', 'notas', 'imagen_alterada','imagen_base64']

            for campo in campos_requeridos:
                if campo not in datos:
                    return func.HttpResponse('Error: El campo {} es requerido.'.format(campo), status_code=400)

            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()

            try:

                query = "SELECT id FROM usuarios WHERE id = %s"
                values = (idUsuario,)

                cursor.execute(query, values)
                
                # Verificar si se encontró un usuario
                id_verificacion = cursor.fetchone()
                if id_verificacion is None:
                    return func.HttpResponse('Error: Usuario no encontrado.', status_code=400)
                else:
                    # Decodifica la imagen
                    imagen_decodificada = base64.b64decode(datos['imagen_base64'])

                    # Insertar un nuevo estudio en la base de datos
                    query = "INSERT INTO Estudios (idUsuario, imagen, json, descripcion, tipo, parte_cuerpo, notas, imagen_alterada, imagen_base64) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    values = (idUsuario, datos['imagen'], datos['json'], datos['descripcion'], datos['tipo'], datos['parte_cuerpo'], datos['notas'], datos['imagen_alterada'], imagen_decodificada)

                    cursor.execute(query, values)

                    try:
                        # Obtener el ID del estudio recién insertado
                        id_estudio = cursor.lastrowid
                    except Exception as e:
                        cnx.rollback()
                        return func.HttpResponse('Error al realizar al consultar el id: {}'.format(str(e)), status_code=500)

                    cnx.commit()

            except Exception as e:
                cnx.rollback()
                return func.HttpResponse('Error al realizar la inserción: {}'.format(str(e)), status_code=500)
            
            finally:
                cursor.close()
                cnx.close()

            # Crear un diccionario con el ID del estudio insertado
            id_return = {'idEstudio': id_estudio}
            
            # Convertir el diccionario a un JSON válido
            json_response = json.dumps(id_return)
            
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse(json_response, status_code=200)
    
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  G E T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        elif req.method == 'GET':
            # Verificamos que exista el idUsuario
            idUsuario = req.params.get('idUsuario')
            if idUsuario is None: return func.HttpResponse('Error: Se requiere el id del usuario.', status_code=400)
            
            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()
            
            # Verificamos si es que hay paginación, si no lo hay, vamos a entregar todos los estudios
            inicio = req.params.get('ini')
            fin = req.params.get('fin')

            try:

                query = "SELECT id FROM usuarios WHERE id = %s"
                values = (idUsuario,)

                cursor.execute(query, values)
                
                # Verificar si se encontró un id de usuario
                id_verificacion = (cursor.fetchone())
                
                if id_verificacion is None:
                    return func.HttpResponse('Error: Usuario no encontrado.', status_code=400)
                
                else:
                    # Consultar los estudios existentes
                    query = "SELECT e.id, e.imagen, e.json, e.descripcion, e.tipo as idTipo, t.tipo, e.parte_cuerpo as idParte, p.parte, e.notas, e.imagen_alterada, e.imagen_base64 FROM Estudios as e INNER JOIN Tipos as t INNER JOIN Partes_cuerpo as p ON e.tipo=t.id and e.parte_cuerpo=p.id WHERE e.idUsuario = %s ORDER BY id DESC "

                    if inicio != None and fin != None:
                        # Tenemos paginación, debemos dar los estudios entre los estudios que nos estan pidiendo
                        query = query + "LIMIT %s OFFSET %s"
                        values = (idUsuario,fin-inicio,inicio)

                    elif inicio != None and fin == None:
                        # Tenemos inicio, pero no tenemo fin, debemos de consultar los estudios desde ese fin hasta el ultimo
                        query = query + "OFFSET %s"
                        values = (idUsuario,inicio)

                    elif inicio == None and fin != None:
                        # No tenemos inicio, pero si fin, debemos tomar desde el primero hasta el limite
                        query = query + "LIMIT %s"
                        values = (idUsuario,fin)

                    else:
                        # No tenemos ni inicio, ni fin, debemos dar todos los estudios
                        values = (idUsuario,)

                    cursor.execute(query, values)

                    columns = [column[0] for column in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))

                    for estudio in results:
                        if estudio['imagen_base64'] is None:
                            estudio['imagen_base64'] =  ''
                        else:
                            estudio['imagen_base64'] =  base64.b64encode(estudio['imagen_base64']).decode('utf-8')

            except Exception as e:
                return func.HttpResponse('Error al realizar la consulta: {}'.format(str(e)), status_code=500)
            
            finally:
                cursor.close()
                cnx.close()
            
            json_response = json.dumps(results)

            return func.HttpResponse(json_response, status_code=200)


    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  P U T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        elif req.method == 'PUT':
            # Pensar cómo implementar la actualización de registros, lo más seguro es que sea 3/4 del post
            return func.HttpResponse("METODO POR INTEGRAR (0-Infinito)", status_code=500)
        else: 
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse("Método no permitido", status_code=400)
        
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  fin  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)
