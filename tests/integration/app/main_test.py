from dotenv import load_dotenv
from app.main import lambda_handler

load_dotenv()


def test_lambda_handler():
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "ticketboat-emails-prod"},
                    "object": {"key": "3r159j21i5q61c8bj8mj91ei6jamc27ftu7hq8o1"},
                }
            }
        ]
    }

    response = lambda_handler(event, {})
    print(response)
