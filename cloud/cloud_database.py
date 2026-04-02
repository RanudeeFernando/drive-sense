import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

class CloudDatabase:
    def __init__(self, table_name=None):
        # Allow override via env var, fallback to constructor arg, then hardcoded default
        self.table_name = table_name or os.environ.get("DYNAMODB_TABLE_NAME", "ParkingSlots")
        
        # Initialize boto3 DynamoDB resource
        try:
            # Credentials are read from environment variables.
            # Set them in a .env file locally, or via an IAM Role on EC2 (no keys needed at all).
            AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
            AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
            REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

            if AWS_ACCESS_KEY and AWS_SECRET_KEY:
                # Local development: use keys from environment
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=REGION,
                    aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY
                )
            else:
                # On EC2 with an IAM Role attached, boto3 picks up credentials automatically
                self.dynamodb = boto3.resource('dynamodb', region_name=REGION)
                
            self.table = self.dynamodb.Table(self.table_name)
            
            # Attempt to reach table (will throw if it doesn't exist or no creds)
            self.table.load()
            print(f"Successfully connected to AWS DynamoDB Table: {self.table_name}")
        except Exception as e:
            print(f"DynamoDB connection error: {e}. Running in local mock mode.")
            self.table = None
            self.storage = {}

    def update_data(self, key, value):
        if self.table is None:
            # Fallback to local dict for testing when not connected
            self.storage[key] = value
            return
            
        try:
            self.table.put_item(
                Item={
                    'SlotKey': str(key),
                    'Data': str(value),
                    'LastUpdated': datetime.now().isoformat()
                }
            )
            print(f"Updated DynamoDB: {key}")
        except Exception as e:
            print(f"Error saving to DB: {e}")

    def retrieve(self):
        if self.table is None:
            return self.storage
            
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            return {item['SlotKey']: item['Data'] for item in items}
        except Exception as e:
            print(f"Error fetching from DB: {e}")
            return {}