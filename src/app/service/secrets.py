import boto3
import json

def get_secret(name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=name)
    
    secret = response['SecretString']
    return json.loads(secret)
