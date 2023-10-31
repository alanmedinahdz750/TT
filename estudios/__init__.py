import mysql.connector
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if req.method == 'POST':
            # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
            datos = req.get_json()
            idUsuario = req.params.get('idUsuario')

            if idUsuario is None: return func.HttpResponse('Error: Se requiere el id del usuario.', status_code=400)

            # Validar que todos los campos requeridos estén presentes en el JSON
            campos_requeridos = ['imagen', 'json', 'descripcion', 'tipo', 'parte_cuerpo', 'notas', 'imagen_alterada']

            for campo in campos_requeridos:
                if campo not in datos:
                    return func.HttpResponse('Error: El campo {} es requerido.'.format(campo), status_code=400)

            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="dicomatetestdb.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()

            try:

                query = "SELECT id FROM usuarios WHERE id = %s"
                values = (idUsuario,)

                cursor.execute(query, values)
                
                # Verificar si se encontró un nombre de usuario
                id_verificacion = cursor.fetchone()
                if id_verificacion is None:
                    return func.HttpResponse('Error: Usuario no encontrado.', status_code=400)
                else:
                    # Insertar un nuevo estudio en la base de datos
                    query = "INSERT INTO Estudios (idUsuario, imagen, json, descripcion, tipo, parte_cuerpo, notas, imagen_alterada) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    values = (idUsuario, datos['imagen'], datos['json'], datos['descripcion'], datos['tipo'], datos['parte_cuerpo'], datos['notas'], datos['imagen_alterada'])

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
        
        elif req.method == 'GET':
            # Verificamos que exista el idUsuario
            idUsuario = req.params.get('idUsuario')
            if idUsuario is None: return func.HttpResponse('Error: Se requiere el id del usuario.', status_code=400)

            # Verificamos si es que hay paginación, si no lo hay, vamos a entregar todos los estudios
            inicio = req.params.get('ini')
            fin = req.params.get('fin')

            if inicio != None and fin != None:

                ''' 
                    NOTA: @Alan, puedes usar este código que una vez hice para implementar la consulta de estudios
                    num = int(num)
                    query = "SELECT mediciones FROM registros WHERE id_zona = %s AND variable = %s ORDER BY cuenta_zona DESC LIMIT %s" '''
                
                # Tenemos paginación, debemos dar los estudios entre los estudios que nos estan pidiendo
                return func.HttpResponse("METODO POR INTEGRAR (INICIO-FIN)", status_code=500)
            elif inicio != None and fin == None:
                # Tenemos inicio, pero no tenemo fin, debemos de consultar los estudios desde ese fin hasta el ultimo
                return func.HttpResponse("METODO POR INTEGRAR (INCIO-Infinito)", status_code=500)
            elif inicio == None and fin != None:
                # No tenemos inicio, pero si fin, debemos tomar desde el primero hasta el limite
                return func.HttpResponse("METODO POR INTEGRAR (0-FIN)", status_code=500)
            else:
                # No tenemos ni inicio, ni fin, debemos dar todos los estudios
                return func.HttpResponse("METODO POR INTEGRAR (0-Infinito)", status_code=500)
            
        elif req.method == 'PUT':
            # Pensar cómo implementar la actualización de registros, lo más seguro es que sea 3/4 del post
            return func.HttpResponse("METODO POR INTEGRAR (0-Infinito)", status_code=500)
        else: 
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse("Método no permitido", status_code=400)
    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)