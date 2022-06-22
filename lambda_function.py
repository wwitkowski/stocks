import json
import requests
import boto3
import os
from decimal import Decimal
from botocore.exceptions import ClientError

dyn_resource = boto3.resource(
    'dynamodb', 
    # aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    # aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    # region_name='us-east-1'
)

def lambda_handler(event, context):
    table = dyn_resource.Table('Stocks')
    table.load()
    item = {
        'date': '2022-06-22',
        'ticker': 'TEST_LAMBDA_NOVARS',
        'p_e': 9,
        'price': 22.12
    }
    table.put_item(
        Item=json.loads(json.dumps(item), parse_float=Decimal)
    )
    return {
        'statusCode': '200',
        'body': json.dumps('Successfully uploaded an item')
    }
