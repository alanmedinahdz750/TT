import mysql.connector
import json
import base64
import azure.functions as func
import hashlib

def generarCodigo(datos):

    idhashed = hashlib.md5(str(datos).encode()).hexdigest()
    idhex = hex(datos)[2:].zfill(6)
    id_compartir = idhex[0:3] + idhashed[3]   +   idhex[3:6] + idhashed[6]

    return id_compartir

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  P O S T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        if req.method == 'POST':
            # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
            idUsuario = req.params.get('idUsuario')
            idEstudio = req.params.get('idEstudio')

            # Validar que todos los campos requeridos estén presentes en el JSON
            if idUsuario is None: return func.HttpResponse('Error: Se requiere el id del usuario.', status_code=400)
            if idEstudio is None: return func.HttpResponse('Error: Se requiere el id del estudio.', status_code=400)

            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()

            try:
                # Verificar que exista usuario
                query = "SELECT id FROM usuarios WHERE id = %s"
                values = (idUsuario,)
                cursor.execute(query, values)
                id_verificacion = cursor.fetchone()

                if id_verificacion is None: return func.HttpResponse('Error: Usuario no encontrado.', status_code=404)

                # Verificar que el estudio exista y no sea del mismo usuario
                query = "SELECT * FROM estudios WHERE id = %s"
                values = (idEstudio,)
                cursor.execute(query, values)
                columns = [column[0] for column in cursor.description] # Pasar los valores a json
                result = dict(zip(columns, cursor.fetchone()))

                if result is None: return func.HttpResponse('Error: Estudio no encontrado.', status_code=404)
                
                # Verifica el id de usuario obtenido y ver si es el mismo que desea al que se copie
                id_verif_usuario = result['idUsuario']
                if id_verif_usuario==idUsuario: return func.HttpResponse('Error: No se puede duplicar el estudio al mismo usuario al que pertenece.', status_code=400)

                # Construye los campos para hacer insert
                campos = []
                valores = []
                porcentaje_s = []
                for columna in columns:
                    if result[columna] and columna.upper()!="ID":   # Se omite el campo id de estudio ya que se autoincrementa en la consulta
                        campos.append(columna)
                        porcentaje_s.append("%s")
                        if columna.upper()=="IDUSUARIO":
                            valores.append(idUsuario)       # Pone el id del usuario al que se desea copiar en vez de el usuario original
                        else:
                            valores.append(result[columna])
                cCampos = ", ".join(campos)
                cPorcentaje_s = ", ".join(porcentaje_s)

                # Construir la consulta SQL final
                if campos:
                    query = "INSERT INTO Estudios (" + cCampos +") VALUES (" + cPorcentaje_s + ")"
                    cursor.execute(query, values)

                    try:
                        # Obtener el ID del estudio recién insertado
                        id_estudio = cursor.lastrowid

                        # Genera el codigo para compartir
                        query = "UPDATE Estudios SET codigo=%s WHERE id=%s"
                        values = (generarCodigo(id_estudio), id_estudio)

                        cursor.execute(query, values)

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
    
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  OTROS  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        else: 
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse("Método no permitido", status_code=400)
        
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  fin  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)
