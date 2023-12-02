import mysql.connector
import json
import azure.functions as func
import base64

def camposConsulta(cadena,campos):

    cCampos = []
    for campo in campos:
        campo = cCampos.append(cadena+campo)
    cCampos = ", ".join(cCampos)

    return cCampos

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  G E T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        if req.method == 'GET':

            # Recibimos los ids y codigos
            idEstudio   = req.params.get('idEstudio')
            nCodigo     = req.params.get('codigo')

            if idEstudio is None and nCodigo is None: return func.HttpResponse('Error: Se requiere el id del estudio o el codigo de compartición.', status_code=400)
                
            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()
            
            try:
                # Armado de consulta
                campos = ["id", "imagen", "descripcion", "notas", "imagen_alterada", "imagen_base64", "codigo", "matriz", "gauss", "brillo", "contraste", "blur", "invertido"]
                query = "SELECT e.tipo as idTipo, t.tipo, e.parte_cuerpo as idParte, p.parte, " + camposConsulta("e.",campos)
                query += " FROM Estudios as e INNER JOIN Tipos as t INNER JOIN Partes_cuerpo as p ON e.tipo=t.id and e.parte_cuerpo=p.id WHERE "

                if idEstudio is not None:
                    query += "e.id = %s "
                    values = (idEstudio,)
                elif nCodigo is not None:
                    query += "e.codigo = %s "
                    values = (nCodigo,)
                else: return func.HttpResponse('Error: Se requiere el id del estudio o el codigo de compartición.', status_code=400)

                # Consultar el estudio
                cursor.execute(query, values)
            
                # Pasar los valores a json
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, cursor.fetchone()))

                if result is None: return func.HttpResponse('Error: Estudio no encontrado.', status_code=404)
                
                # Se codifica la imagen si es encontrada
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
                      
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  P O S T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        elif req.method == 'POST':

            # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
            datos = req.get_json()
            idEstudio = req.params.get('idEstudio')
            if idEstudio is None: return func.HttpResponse('Error: Se requiere el id del estudio.', status_code=400)

            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()

            try:

                # Verificar que el estudio exista y no sea del mismo usuario
                query = "SELECT * FROM estudios WHERE id = %s"
                values = (idEstudio,)
                cursor.execute(query, values)

                # Verificar si se encontró un usuario
                id_verificacion = cursor.fetchone()
                if id_verificacion is None: return func.HttpResponse('Error: Estudio no encontrado.', status_code=404)

                # Decodifica la imagen si la encuentra
                if 'imagen_base64' in datos:
                    datos['imagen_base64'] = base64.b64decode(datos['imagen_base64'])

                # Construye los campos para hacer insert
                campos = list(datos.keys())
                sets = []
                values = []
                for campo in campos:
                    if campo.upper()!="ID":   # Se omite el campo id de estudio ya que se autoincrementa en la consulta
                        sets.append(campo + " = %s")
                        values.append(datos[campo])
                cSets = ", ".join(sets)
                values.append(idEstudio)                 # Agrega el id para el "WHERE id=%s"

                if campos:
                    query = "UPDATE Estudios SET " + cSets + " WHERE id=%s"
                    cursor.execute(query, values)
                    cnx.commit()

            except Exception as e:
                cnx.rollback()
                return func.HttpResponse('Error al actulizar: {}'.format(str(e) +" Datos: " +datos), status_code=500)

            finally:
                cursor.close()
                cnx.close()

            # Enviar la respuesta HTTP con el id
            return func.HttpResponse("Estudio con id: {}, Actualizado".format(str(idEstudio)), status_code=200)
        
     #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  D E L E T E  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        elif req.method == 'DELETE':

            # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
            datos = req.get_json()
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

            except Exception as e:
                cnx.rollback()
                return func.HttpResponse('Error al borrar: {}'.format(str(e)), status_code=500)
            
            finally:
                cursor.close()
                cnx.close()
            
            # Enviar la respuesta HTTP con el id
            return func.HttpResponse("Estudio con id: {}, Borrado".format(str(idEstudio)), status_code=200)
                   
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  O T R O S  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        else: 
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse("Método no permitido", status_code=405)
        
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  fin  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)
