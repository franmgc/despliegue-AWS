import configparser
import boto3
import os
import requests
import json

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# credentials = readCredentials()

# os.environ['AWS_ACCESS_KEY_ID'] = credentials[0]
# os.environ['AWS_SECRET_ACCESS_KEY'] = credentials[1]
# os.environ['AWS_SESSION_TOKEN'] = credentials[2]
# os.environ['AWS_DEFAULT_REGION'] = 'us-east-1' 




def readCredentials():
    # Specify the path to the AWS credentials file

    aws_credentials_file_path = "aws/credentials"
    # aws_credentials_file_path = "../aws/credentials"

    # Expand the path and create a ConfigParser object
    config = configparser.ConfigParser()
    config.read(aws_credentials_file_path)

    # Check if the "default" section (profile) exists in the credentials file
    if "default" in config:

        # Get the Access Key ID and Secret Access Key
        access_key_id = config["default"]["aws_access_key_id"]
        secret_access_key = config["default"]["aws_secret_access_key"]
        session_token = config["default"]["aws_session_token"]


        os.environ['AWS_ACCESS_KEY_ID'] = access_key_id
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret_access_key
        os.environ['AWS_SESSION_TOKEN'] = session_token
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1' 

        print("[CREDENTIALS] ---> OK")



        # return([access_key_id, secret_access_key, session_token])

    else:
        print("No 'default' profile found in the AWS credentials file.")









##############################################################
########################### SQS ##############################
##############################################################


def crearSQS(nombre_cola):
    sqs = boto3.client('sqs')
    response = sqs.create_queue(
        QueueName=nombre_cola,
        Attributes={
            'FifoQueue': 'true',  # Marcar la cola como FIFO
            'ContentBasedDeduplication': 'true',  # Habilitar la deduplicación basada en contenido
            'VisibilityTimeout' : '60'
        }
    )

    print('[SQS] ---> Cola creada con exito!')


    return response["QueueUrl"]




def enviarSQS(cola_URL, mensaje):

    # queue_url = "https://sqs.us-east-1.amazonaws.com/621668821568/prueba.fifo"

    # Create an SQS client
    sqs = boto3.client('sqs')

    try:
        # Send a message to the FIFO SQS queue
        response = sqs.send_message(
            QueueUrl=cola_URL,
            MessageBody=mensaje,
            MessageGroupId='my-group',
            # MessageDeduplicationId='unique-id'
        )
        print('[SQS] ---> Mensaje enviado')

    except Exception as e:
        print(f"An error occurred: {e}")
        
        
def leerSQS(cola_URL):
    # URL de la cola SQS FIFO (reemplaza con la URL de tu cola)
    sqs = boto3.client('sqs')


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


            # Borra el mensaje de la cola después de procesarlo

            sqs.delete_message(
                QueueUrl=cola_URL,
                ReceiptHandle=receipt_handle
            )
            print('[SQS] ---> Mensaje leido')
        

    # else:
    #     print('No se recibieron mensajes en la cola.')








##############################################################
########################### s3  ##############################
##############################################################

def crearBucket(nombre_bucket):
 
    s3 = boto3.client('s3')
    s3.create_bucket(Bucket=nombre_bucket)
    print('[S3] ---> Bucket creado con exito!')







def subirDataBucket(bucket_name, pdf_name, local_pdf):
    # Sube el archivo PDF al bucket
    s3 = boto3.resource('s3')
    # s3.Object(bucket_name, 'hello.txt').put(Body=open('/tmp/hello.txt', 'rb'))
    s3.Object(bucket_name, pdf_name).put(Body=open(local_pdf, 'rb'))
    print("[S3] ---> Archivo subido con exito")



def accederBucket(bucket_name, archivo_S3, archivo_local):
    s3 = boto3.resource('s3')
 
    # Descarga el archivo PDF
    try:
        s3.Bucket(bucket_name).download_file(archivo_S3, archivo_local)
        # s3.download_file(bucket_name, archivo_S3, archivo_local)  # El último argumento es el nombre de archivo de destino
        print("[S3] ---> Accedido Bucket")

    except Exception as e:
        print(f'Ocurrió un error al descargar el archivo PDF: {str(e)}')

    

def eliminarBucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    
    for key in bucket.objects.all():
        key.delete()
    bucket.delete()

    print("[S3] ---> Bucket eliminado con exito")



def getURL(bucket_name, object_name, expiration):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=expiration)


    # The response contains the presigned URL
    return response



##############################################################
######################## dynamodb ############################
##############################################################



def buy_concert_tickets(concert_name, tickets_to_buy):
    dynamodb = boto3.resource('dynamodb')
    table_name = 'ConcertsTable'

    # Create a DynamoDB table reference
    table = dynamodb.Table(table_name)

    try:
        # Define the condition expression
        condition_expression = "RemainingTickets >= :tickets_to_buy"

        # Define the expression attribute values
        expression_attribute_values = {
            ":tickets_to_buy": tickets_to_buy,
        }

        # Perform a conditional update
        response = table.update_item(
            Key={
                'ConcertName': concert_name
            },
            UpdateExpression="SET RemainingTickets = RemainingTickets - :tickets_to_buy",
            ConditionExpression=condition_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"  # Return the updated item
        )

        updated_item = response.get('Attributes', None)

        if updated_item:
            print(f"Successfully bought {tickets_to_buy} tickets for {concert_name}. Updated item: {updated_item}")
            return True
        else:
            print(f"Not enough tickets available for {concert_name} to buy {tickets_to_buy} tickets.")
            return False

    except Exception as e:
        print(f"Error: No quedan disponibles tantas entradas para", concert_name)
        print(e)
        return False





def creatTable():

    # Initialize a session using Amazon DynamoDB
    dynamodb = boto3.resource('dynamodb')

    # Define the table name and schema
    table_name = 'ConcertsTable'
    partition_key = 'ConcertName'

    # Create the DynamoDB table
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': partition_key,
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': partition_key,
                'AttributeType': 'S'  # String
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,  # Adjust as needed
            'WriteCapacityUnits': 5  # Adjust as needed
        }
    )

    # Wait for the table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

    # Add concert data to the table
    concerts_data = [
        {"ConcertName": "Pink Floyd", "RemainingTickets": 100},
        {"ConcertName": "Imagine Dragons", "RemainingTickets": 150},
        {"ConcertName": "Ariana Grande", "RemainingTickets": 75},
        {"ConcertName": "Adele", "RemainingTickets": 200}
    ]

    table = dynamodb.Table(table_name)

    with table.batch_writer() as batch:
        for concert in concerts_data:
            batch.put_item(Item=concert)

    print(f"Table '{table_name}' created and populated with data.")




##############################################################
########################### PDF ##############################
##############################################################


def generarPDF(nombrePDF, nombre_comprador, evento, num_entradas):

    # Create a PDF document
    document = SimpleDocTemplate(nombrePDF, pagesize=letter)


    # Create a list to hold the contents of the PDF
    content = []

    # Create a style for the document
    styles = getSampleStyleSheet()
    style = styles["Normal"]

    # Add a title to the PDF
    title = Paragraph("Entradas:", styles["Title"])
    content.append(title)
    content.append(Spacer(1, 12))  # Add some space

    # Add some text to the PDF
    text = "Aqui tienes tus entradas!"
    content.append(Paragraph(text, style))
    content.append(Spacer(1, 20))  # Add some space

    # Create a table
    data = [["Comprador", "Evento", "Nº entradas"],
            [nombre_comprador, evento, num_entradas]]
    table = Table(data, colWidths=[2*inch, 1*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(table)

    content.append(Spacer(1, 20))  # Add some space

    # Add an image to the PDF
    image_path = "templates/concierto.jpg"  # Replace with the actual path to your image file
    image = Image(image_path, width=3*inch, height=2*inch)
    content.append(image)
    content.append(Spacer(1, 12))  # Add some space






    # Build the PDF document
    document.build(content)

    print(f"[PDF] ---> Documento creado: {nombrePDF}")










'''    
MENSAJE SQS REQUEST:
    - ID del usuario que hace la peticion/ID de la sesion
    - Nombre del Evento
    - Numero de entradas

MENSAJE SQS RESPONSE:
    - ID del usuario/ID de la sesion
    - Confirmacion/Error -> Numero de confirmacion que se asocia a las entradas
'''