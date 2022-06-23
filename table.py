import json
import logging
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DynamoDBTable:
    table_name = None
    
    """Encapsulates an Amazon DynamoDB table."""
    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.table = None

    def exists(self):
        """
        Determines whether a table exists. As a side effect, stores the table in
        a member variable.
        :param table_name: The name of the table to check.
        :return: True when the table exists; otherwise, False.
        """
        try:
            table = self.dyn_resource.Table(self.table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                exists = False
            else:
                logger.error(
                    "Unable to check if table %s exists. %s: %s", self.table_name, 
                    err.response['Error']['Code'], err.response['Error']['Message']
                )
                raise
        else:
            self.table = table
        return exists

    def write_batch(self, items: list):
        """
        Fills an Amazon DynamoDB table with the specified data, using the Boto3
        Table.batch_writer() function to put the items in the table.
        Inside the context manager, Table.batch_writer builds a list of
        requests. On exiting the context manager, Table.batch_writer starts sending
        batches of write requests to Amazon DynamoDB and automatically
        handles chunking, buffering, and retrying.
        :param items: The data to put in the table. Each item must contain at least
                       the keys required by the schema that was specified when the
                       table was created.
        """
        try:
            with self.table.batch_writer() as writer:
                for item in items:
                    writer.put_item(Item=json.loads(json.dumps(item), parse_float=Decimal))
        except ClientError as err:
            logger.error(
                "Couldn't load data into table %s. %s: %s", self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return json.dumps('Successfully uploaded %s items', len(items))

    def add_item(self, item: dict):
        """
        Adds a item to the table.
        :param item: The item to be added
        """
        try:
            parsed_item = json.loads(json.dumps(item), parse_float=Decimal)
            self.table.put_item(Item=parsed_item)
        except ClientError as err:
            logger.error(
                "Couldn't add item to the table. %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return json.dumps(item)

    def get_item(self, key: dict):
        """
        Gets movie data from the table for a specific movie.
        :param key: Key of the item in the database.
        :return: Item data.
        """
        try:
            response = self.table.get_item(Key=key)
        except ClientError as err:
            logger.error(
                "Couldn't get item %s. %s: %s", key,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Item']


class Stocks(DynamoDBTable):
    table_name = 'Stocks'