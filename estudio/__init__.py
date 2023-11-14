import mysql.connector
import json
import azure.functions as func
import base64

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  G E T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        if req.method == 'GET':
            # Verificamos que exista el idUsuario
            idEstudio = req.params.get('idEstudio')
            if idEstudio is None: return func.HttpResponse('Error: Se requiere el id del estudio.', status_code=400)
            
            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()
            
            try:
                # Consultar el estudio 
                query = "SELECT e.id, e.imagen, e.json, e.descripcion, e.tipo as idTipo, t.tipo, e.parte_cuerpo as idParte, p.parte, e.notas, e.imagen_alterada, e.imagen_base64 FROM Estudios as e INNER JOIN Tipos as t INNER JOIN Partes_cuerpo as p ON e.tipo=t.id and e.parte_cuerpo=p.id WHERE e.id = %s"
                values = (idEstudio,)

                cursor.execute(query, values)
            
                # Pasar los valores a json
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, cursor.fetchone()))

                if result is None:
                    return func.HttpResponse('Error: Estudio no encontrado.', status_code=400)

                if result['imagen_base64'] is None:
                    result['imagen_base64'] =  ''
                else:
                    result['imagen_base64'] =  base64.b64encode(result['imagen_base64']).decode('utf-8')
                    
                cnx.commit()

            except Exception as e:
                return func.HttpResponse('Error al realizar la consulta: {}'.format(str(e)), status_code=500)
            
            finally:
                cursor.close()
                cnx.close()
            
            json_response = json.dumps(result)

            return func.HttpResponse(json_response, status_code=200)
            
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  G E T   C O M P A R T I D O  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        if req.method == 'GET':
            # Verificamos que exista el idUsuario
            idEstudio = req.params.get('idEstudio')
            idUsuario = req.params.get('idUsuario')
            if idEstudio is None: return func.HttpResponse('Error: Se requiere el id del estudio.', status_code=400)
            if idUsuario is None: return func.HttpResponse('Error: Se requiere el id del estudio.', status_code=400)
            
            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()
            
            try:
                # Consultar el estudio
                query = "SELECT e.id, e.imagen, e.json, e.descripcion, e.tipo as idTipo, t.tipo, e.parte_cuerpo as idParte, p.parte, e.notas, e.imagen_alterada, e.imagen_base64 FROM Estudios as e INNER JOIN Tipos as t INNER JOIN Partes_cuerpo as p ON e.tipo=t.id and e.parte_cuerpo=p.id WHERE e.id = %s"
                values = (idEstudio,)
                cursor.execute(query, values)
            
                # Pasar los valores a json
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, cursor.fetchone()))
                
                if result is None: return func.HttpResponse('Error: Estudio no encontrado.', status_code=204)

                # Consultar los estudios existentes
                query = "SELECT permiso FROM Compartidos WHERE idEstudio = %s and (idUsuario = %s or idUsuario ='ALL')"
                values = (idEstudio,idEstudio,)
                cursor.execute(query, values)
                nPermiso = cursor.fetchone()
                
                # Ve si la persona tiene el permiso correcto, si no lo tiene devuelve 
                if nPermiso==0 or nPermiso is None: return func.HttpResponse('No tiene el permiso necesario para ver el estudio', status_code=403)
                    
                # Agrega el tipo de permiso a la consulta
                result['permiso'] = nPermiso
                
                # Decodifica la imagen
                if result['imagen_base64'] is None:
                    result['imagen_base64'] =  ''
                else:
                    result['imagen_base64'] =  base64.b64encode(result['imagen_base64']).decode('utf-8')

                cnx.commit()
                    
            except Exception as e:
                return func.HttpResponse('Error al realizar la consulta: {}'.format(str(e)), status_code=500)
            
            finally:
                cursor.close()
                cnx.close()
            
            json_response = json.dumps(result)

            return func.HttpResponse(json_response, status_code=200)


    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  O T R O S  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        else: 
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse("Método no permitido", status_code=400)
        
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  fin  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)
