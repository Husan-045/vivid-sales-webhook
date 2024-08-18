import boto3


class CloudwatchMonitor:
    def __init__(self, client):
        self.client = client

    def send_success_to_cloudwatch(self):
        # Implementation to send success metric to CloudWatch
        pass


def lambda_handler(event, context):
    try:
        print(event)
        CloudwatchMonitor(boto3.client("cloudwatch")).send_success_to_cloudwatch()

        return {"statusCode": 200, "body": "Done"}
    except Exception as e:
        print("Error sending", e)
        raise e
