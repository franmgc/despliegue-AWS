import configparser
import boto3
import os
import time
import paramiko
from scp import SCPClient, SCPException
import myModuleAWS

# -------------- IPs elasticas -------------- 

IP_FRONT = '54.159.166.197' 

IP_BACK1 = '34.230.251.17'

IP_BACK2 = '34.225.145.85'

usuario_ssh = 'ubuntu'
# --------------------------------------------

# -------------- CREAR RECURSOS -------------- 



config = configparser.ConfigParser()
config.read("credentials")

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
else:
    print("No 'default' profile found in the AWS credentials file.")
######## BUCKET S3

nombre_bucket = "bucketholaentradas"
myModuleAWS.crearBucket(nombre_bucket)


######## COLAS SQS

URL_cola_hacia_front = myModuleAWS.crearSQS("ColaHaciaFront.fifo")
URL_cola_hacia_back = myModuleAWS.crearSQS("ColaHaciaBack.fifo")
URL_cola_hacia_back = "https://sqs.us-east-1.amazonaws.com/621668821568/ColaHaciaBack.fifo"
URL_cola_hacia_front = "https://sqs.us-east-1.amazonaws.com/621668821568/ColaHaciaFront.fifo"


# --------------------------------------------
ec2 = boto3.client('ec2')

ec2.start_instances(
    InstanceIds=[
        'i-037ae9a8886d7faae',
        'i-06f56abd3dc4576c9',
        'i-00d49a772e0336f39'
    ])

print("[DynamoDB] ---> OK")
print("[EC2] RESTARTED")

time.sleep(60)


print("Actualizando las credenciales de las maquinas EC2...")
k = paramiko.RSAKey.from_private_key_file("front.pem")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(hostname=IP_FRONT, username=usuario_ssh, pkey=k, allow_agent=False, look_for_keys=False) 
sftp = c.open_sftp() 
sftp.put('credentials', '/home/ubuntu/despliegue-AWS/aws/credentials') 
sftp.close()
c.exec_command("cd /home/ubuntu/despliegue-AWS && nohup python3 frontend.py > output.log &")
c.close()

print("[FRONTEND] OK")



k = paramiko.RSAKey.from_private_key_file("back1.pem")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(hostname=IP_BACK1, username=usuario_ssh, pkey=k, allow_agent=False, look_for_keys=False) 
sftp = c.open_sftp() 
sftp.put('credentials', '/home/ubuntu/despliegue-AWS/aws/credentials') 
sftp.close()
c.exec_command("cd /home/ubuntu/despliegue-AWS && nohup python3 backend.py > output.log &")
c.close()

print("[BACKEND 1] OK")



k = paramiko.RSAKey.from_private_key_file("back2.pem")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(hostname=IP_BACK2, username=usuario_ssh, pkey=k, allow_agent=False, look_for_keys=False) 
sftp = c.open_sftp() 
sftp.put('credentials', '/home/ubuntu/despliegue-AWS/aws/credentials') 
sftp.close()
c.exec_command("cd /home/ubuntu/despliegue-AWS && nohup python3 backend.py > output.log &")
c.close()

print("[BACKEND 2] OK")





