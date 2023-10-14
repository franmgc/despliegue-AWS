import myModuleAWS
import boto3
import json
import os


##############################################################
########################### INIT #############################
##############################################################



myModuleAWS.readCredentials()

nombre_bucket = "bucketholaentradas"
myModuleAWS.crearBucket(nombre_bucket)


sqs = boto3.client('sqs')
URL_cola_hacia_front = myModuleAWS.crearSQS("ColaHaciaFront.fifo")
cola_URL = "https://sqs.us-east-1.amazonaws.com/621668821568/ColaHaciaBack.fifo"

##############################################################
##############################################################
##############################################################

while True:

    # myModuleAWS.leerSQS(queue_url)





    # Recibe mensajes de la cola SQS
    response = sqs.receive_message(
        QueueUrl=cola_URL,
        MaxNumberOfMessages=1,  # Número máximo de mensajes a recibir
        AttributeNames=['All'],  # Para recibir todos los atributos de mensaje
        MessageAttributeNames=['All'],  # Para recibir todos los atributos de mensaje
        VisibilityTimeout=60,  # Tiempo de espera para recibir mensajes
        WaitTimeSeconds=0  # Tiempo de espera para recibir mensajes
    )

    # Verifica si se han recibido mensajes
    if 'Messages' in response:
        for message in response['Messages']:
            message_body = message['Body']
            receipt_handle = message['ReceiptHandle']
            
            print("---------------------")
            # Procesa el mensaje
            print(f'Mensaje recibido: {message_body}')


            # Parse the JSON string
            data = json.loads(message_body)


            # Borra el mensaje de la cola después de procesarlo
            sqs.delete_message(
                QueueUrl=cola_URL,
                ReceiptHandle=receipt_handle
            )
            print('[SQS] ---> Mensaje Borrado')

            # Access values by their keys
            uuid = data["uuid"]
            print(uuid)

            nombre_comprador = data["nombre_comprador"]
            print(nombre_comprador)

            num_tickets = data["num_tickets"]
            print(num_tickets)

            evento = data["evento"]
            print(evento)            

            vendida = myModuleAWS.buy_concert_tickets(evento, int(num_tickets))


            if(not vendida):

                myModuleAWS.enviarSQS(URL_cola_hacia_front, "......")
                print("[INFO] Cliente informado")
                break



            # myModuleAWS.generarPDF("../pdf/ticket_"+uuid+".pdf", nombre_comprador, evento , num_tickets)
            myModuleAWS.generarPDF("ticket_"+uuid+".pdf", nombre_comprador, evento , num_tickets)
            
            myModuleAWS.subirDataBucket(nombre_bucket, "ticket_"+uuid+".pdf" ,"ticket_"+uuid+".pdf")
            os.remove("ticket_"+uuid+".pdf")
            print("[PDF] Subido & Borrado")

            url_ticket = myModuleAWS.getURL(nombre_bucket, "ticket_"+uuid+".pdf", 3600)

            print(url_ticket)



            # generarPDF()
            


            myModuleAWS.enviarSQS(URL_cola_hacia_front, url_ticket+"#####"+uuid)



        

    # else:
    #     print('No se recibieron mensajes en la cola.')







       
           




       