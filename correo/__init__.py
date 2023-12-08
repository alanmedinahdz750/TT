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
            if idUsuario is None and cCorreo is None: return func.HttpResponse('Error: Se requiere el id del usuario.', status_code=400)

            # Conexión a la base de datos
            cnx = mysql.connector.connect(user="dicomate", password="trabajoterminal1$", host="db-dicomate.mysql.database.azure.com", port=3306, database="TT", ssl_disabled=False)
            cursor = cnx.cursor()

            try:

                # Verificar que el estudio exista y no sea del mismo usuario
                query = "SELECT * FROM usuarios WHERE id = %s"
                values = (idUsuario,)
                cursor.execute(query, values)

            
                # create message object instance 
                msg = MIMEMultipart()
                message = "Thank you"
                
                # setup the parameters of the message 
                password = "your_password"
                msg['From'] = "your_address"
                msg['To'] = "to_address"
                msg['Subject'] = "Subscription"
                
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
                print("successfully sent email to %s:" % (msg['To']))

            except Exception as e:
                return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  O T R O S  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        else: 
            # Enviar la respuesta HTTP con el JSON
            return func.HttpResponse("Método no permitido", status_code=405)
        
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  fin  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)