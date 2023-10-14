from flask import Flask, render_template, request

import json
import uuid
import boto3
import time
import myModuleAWS




##############################################################
########################### INIT #############################
##############################################################


myModuleAWS.readCredentials()

URL_cola_hacia_back = myModuleAWS.crearSQS("ColaHaciaBack.fifo")

URL_cola_hacia_front = "https://sqs.us-east-1.amazonaws.com/621668821568/ColaHaciaFront.fifo"

sqs = boto3.client('sqs')

##############################################################
##############################################################
##############################################################


app = Flask(__name__)

# Creating simple Routes 
@app.route('/test')
def test():
    return "Home Page"

@app.route('/test/about/')
def about_test():
    return "About Page"



# Routes to Render Something
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")
methods=['POST']


@app.route('/comprar', methods=['GET', 'POST'])
def comprar():

    evento = request.form['campo_oculto']

    return render_template("comprar.html", mensaje=evento)




@app.route('/about', strict_slashes=False)
def about():
    return render_template("about.html")


@app.route('/procesar_compra', methods=['GET', 'POST'])
def procesar_compra():
    nombre = request.form.get('nombre')
    evento = request.form.get('campo_oculto')
    numero_entradas = request.form.get('numero_entradas')

    uuid_random =str(uuid.uuid4())
    paquete = {
        "uuid": uuid_random,
        "nombre_comprador": nombre,
        "num_tickets": numero_entradas,  # Replace with your desired number
        "evento": evento  # Replace with your desired name
    }

    print(json.dumps(paquete))

    myModuleAWS.enviarSQS(URL_cola_hacia_back, json.dumps(paquete))

    print('Esperando Back...')
    while True:
            
        response = sqs.receive_message(
            QueueUrl=URL_cola_hacia_front,
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
                # print(f'Mensaje recibido: {message_body}')

                print(message_body)


                if message_body=="......":
                    print("[INFO] Has comprado muchas entradas")
                    sqs.delete_message(
                        QueueUrl=URL_cola_hacia_front,
                        ReceiptHandle=receipt_handle
                    )

                    print('[SQS] ---> Mensaje borrado')
                    return render_template("fallo.html")


                message = message_body.split('#####')[0]
                id_user =  message_body.split('#####')[1]


                print(message)
                print('---------')
                print(id_user)
                # if uuid == uid
                if id_user == uuid_random:
                    sqs.delete_message(
                        QueueUrl=URL_cola_hacia_front,
                        ReceiptHandle=receipt_handle
                    )

                    print('[SQS] ---> Mensaje borrado')
                
                else: 
                    response = sqs.change_message_visibility(
                                    QueueUrl=URL_cola_hacia_front,
                                    ReceiptHandle=receipt_handle,
                                    VisibilityTimeout=0
                                    )
                    
                    print('[SQS] ---> Mensaje actualizado')




                print('[SQS] ---> Mensaje leido')
                # else visibity timeout=0
                

                return render_template("exito.html", mensaje=message)
        
        else: continue
    



    


# Make sure this we are executing this file
if __name__ == '__main__':
    app.run(debug=True)
