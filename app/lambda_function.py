import os
import requests
import boto3
from .table import Stocks

dyn_resource = boto3.resource(
    'dynamodb', 
    # aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    # aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    # region_name='us-east-1'
)

def lambda_handler(event, context):
    item = {
        'date': '2022-06-23',
        'ticker': 'TEST',
        'p_e': 9,
        'price': 22.12
    }
    table = Stocks(dyn_resource)
    if table.exists():
        r = table.add_item(item)
    return {
        'statusCode': '200',
        'body': r
    }