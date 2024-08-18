from unittest.mock import MagicMock, patch

from app.cloudwatch_monitor import CloudwatchMonitor


def test_send_success_to_cloudwatch():
    # Mock the cloudwatch client
    mock_cloudwatch = MagicMock()

    # Create a CloudwatchMonitor instance with the mock cloudwatch client
    cloudwatch_monitor = CloudwatchMonitor(mock_cloudwatch)

    # Mock environment variables
    with patch.dict(
        "os.environ",
        {
            "CLOUDWATCH_MONITOR_NAMESPACE": "TestNamespace",
            "ENVIRONMENT": "TestEnvironment",
        },
    ):
        # Call the send_success_to_cloudwatch method
        cloudwatch_monitor.send_success_to_cloudwatch()

        # Check if put_metric_data was called on the mock cloudwatch client with the expected arguments
        mock_cloudwatch.put_metric_data.assert_called_once_with(
            Namespace="TestNamespace",
            MetricData=[
                {
                    "MetricName": "success",
                    "Value": 1,
                    "Unit": "Count",
                    "Dimensions": [{"Name": "environment", "Value": "TestEnvironment"}],
                }
            ],
        )
