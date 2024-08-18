import urllib.parse

import boto3


class CloudwatchMonitor:
    def __init__(self, client):
        self.client = client

    def send_success_to_cloudwatch(self):
        # Implementation to send success metric to CloudWatch
        pass


def lambda_handler(event, context):
    try:
        body = event["body"]

        parsed_body = urllib.parse.parse_qs(body)
        readable_body = {k: v[0] for k, v in parsed_body.items()}
        print(readable_body)
        v = {'orderid': '66797246', 'token': 'e66756a3-2a38-4c9e-9721-25319ff5ab0a', 'quantity': '1',
             'ticketid': '767215502', 'total': '155.04', 'section': 'GA PIT', 'row': 'GA1',
             'event': 'Falling In Reverse',
             'venue': 'Ford Idaho Center - Nampa, ID', 'date': '2024-08-18 17:45:00', 'barCodesRequired': 'false',
             'inHandDate': '0000-00-00', 'instantDownload': 'false', 'electronic': 'true', 'instantFlashSeats': 'false',
             'instantTransfer': 'false'}
        CloudwatchMonitor(boto3.client("cloudwatch")).send_success_to_cloudwatch()

        return {"statusCode": 200, "body": "Done"}
    except Exception as e:
        print("Error sending", e)
        raise e
