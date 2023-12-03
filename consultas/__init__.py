import mysql.connector
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:

    try:
        if req.method == 'GET':

            # Recibe los parametros
            nId = req.params.get('id')
            tabla = req.params.get('tabla')
            datos = req.get_json()

            # Valida parametros
            tablas = ["areas", "estudios", "estudios_orthanc", "partes_cuerpo", "tipos", "universidades"]
            if tabla is None: func.HttpResponse('Error: Necesita una tabla a consultar.', status_code=400)
            if tabla not in tablas: func.HttpResponse('Error: Tabla no autorizada o no encontrada.', status_code=400)
            if datos: 
                if 'campos' not in datos: return func.HttpResponse('Error: Si consulta campos en especifico adjunte "datos" en un jason con un arreglo de campos.'.format(campo), status_code=400)

            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()
            
            try:
                # Toma los campos a consultar
                campos = '*'
                if datos:
                    campos = ' ,'.join(datos['campos'])

                # Construye consulta
                query = "SELECT " + campos + " FROM " + tabla

                # Modifica consulta si consulta id
                values = []
                if nId:
                    query += " WHERE id = %s"
                    values = (nId,)

                # Ejecuta consulta
                cursor.execute(query, values)
            
                # Pasar los valores a json
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                if results is None: return func.HttpResponse('No hay resultados.', status_code=404)

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
            return func.HttpResponse("Método no permitido", status_code=400)
        
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  fin  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)
