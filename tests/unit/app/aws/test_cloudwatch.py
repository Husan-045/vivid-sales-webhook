import os
import unittest
from unittest.mock import Mock, patch

from app.aws.cloudwatch_monitor import CloudwatchMonitor


class MyTestCase(unittest.TestCase):
    @patch("boto3.client")
    @patch.dict(os.environ, {"CLOUDWATCH_NAMESPACE": "test_namespace", "ENVIRONMENT": "test_environment"})
    def test_send_success_to_cloudwatch(self, mock_boto_client):
        cloudwatch_monitor = CloudwatchMonitor(mock_boto_client())

        # Mock the put_metric_data method of the CloudWatch client
        mock_put_metric_data = Mock()
        mock_boto_client.return_value.put_metric_data = mock_put_metric_data

        # Call the method you want to test
        cloudwatch_monitor.send_success_to_cloudwatch()

        # Assert that the put_metric_data method was called with the correct parameters
        mock_put_metric_data.assert_called_once_with(
            Namespace="test_namespace",
            MetricData=[
                {
                    "MetricName": "Success",
                    "Value": 1,
                    "Unit": "Count",
                    "Dimensions": [
                        {"Name": "Environment", "Value": "test_environment"},
                    ],
                }
            ],
        )


