import os

import boto3


class CloudwatchMonitor:
    def __init__(self, cloudwatch):
        self.cloudwatch = cloudwatch

    def send_success_to_cloudwatch(self):
        self.cloudwatch.put_metric_data(
            Namespace=os.environ["CLOUDWATCH_NAMESPACE"],
            MetricData=[
                {
                    "MetricName": "Success",
                    "Value": 1,
                    "Unit": "Count",
                    "Dimensions": [
                        {"Name": "Environment", "Value": os.environ["ENVIRONMENT"]},
                    ],
                }
            ],
        )


def get_cloudwatch_monitor():
    return CloudwatchMonitor(boto3.client("cloudwatch"))
