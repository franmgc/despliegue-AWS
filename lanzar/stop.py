import configparser
import boto3
import os
import time
import paramiko
from scp import SCPClient, SCPException
import myModuleAWS




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









# Crear una conexión al servicio EC2.
ec2 = boto3.client('ec2')

# Detener la instancia EC2.
ec2.stop_instances(
    InstanceIds=[
        'i-037ae9a8886d7faae',
        'i-06f56abd3dc4576c9',
        'i-00d49a772e0336f39'
    ])


