import os
import uuid
from datetime import datetime, timezone

import boto3


def upload_to_s3_for_snowflake(table_name, csv_data):
    s3 = boto3.client("s3", region_name="us-east-1")
    now = datetime.now(tz=timezone.utc)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    hour = now.hour

    file_key = f"{os.getenv('ENVIRONMENT')}/{table_name}/{year}/{month}/{day}/{hour}/{str(uuid.uuid4())}.csv"

    s3.put_object(Bucket="ticketboat-event-data", Key=file_key, Body=csv_data)
    print("CSV Upload Successful")
