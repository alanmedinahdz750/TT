import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import mysql.connector
import json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:


    try:

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  G E T  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        if req.method == 'GET': 
            
            idUsuario = req.params.get('idUsuario')
            cCorreo = req.params.get('correo')
            if idUsuario is None and cCorreo is None: return func.HttpResponse('Error: Se requiere el id del usuario o el correo.', status_code=400)

            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()

            try:

                # Verificar que el estudio exista y no sea del mismo usuario
                query = "SELECT contrasena, correo FROM usuarios"
                if idUsuario is not None:
                    query += "WHERE id = %s"
                    values = (idUsuario,)
                else:
                    query += "WHERE correo = %s"
                    values = (cCorreo,)
                cursor.execute(query, values)

                                # Pasar los valores a json
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, cursor.fetchone()))

                cContrasena = result['contrasena']
                cCorreo = result['correo']

                if cContrasena is None or cCorreo is None: return func.HttpResponse('Error: Usuario o correo no encontrado', status_code=404)

                # create message object instance 
                msg = MIMEMultipart()
                message = "Se ha solicitado un correo para restablecer la contraseña para su acceso a Dicomate, la contraseña es: " + cContrasena + " Si usted no la ha solicitado, haga caso omiso a este mensaje"
                
                # setup the parameters of the message 
                password = "shejxlcguetihzag"
                msg['From'] = "dicomate.noreply@gmail.com"
                msg['To'] = cCorreo
                msg['Subject'] = "Reestablecimiento de su contraseña de Dicomate"
                
                # add in the message body 
                msg.attach(MIMEText(message, 'plain'))
                
                #create server 
                server = smtplib.SMTP('smtp.gmail.com: 587')
                server.starttls()
                
                # Login Credentials for sending the mail 
                server.login(msg['From'], password)
                
                # send the message via the server. 
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                server.quit()
                # print("successfully sent email to %s:" % (msg['To']))

            except Exception as e:
                return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)

            finally:
                cnx.close()

            return func.HttpResponse('Correo enviado a: {}'.format(msg['To']), status_code=200)
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  O T R O S  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        else: 
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse("Método no permitido", status_code=405)
        
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  fin  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)
        
