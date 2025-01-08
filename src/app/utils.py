import os
import time
from functools import wraps
from typing import Type, Tuple, Union

import boto3

sqs_client = boto3.client('sqs')
dynamodb_resource = boto3.resource('dynamodb')
queue_url = os.getenv('SQS_CSV_QUEUE_URL')

def retry_on_exception(
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]],
        max_attempts: int = 5,
        initial_wait: float = 1,
        backoff_factor: float = 2,
        should_retry_func: callable = None
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            wait_time = initial_wait
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts or (should_retry_func and not should_retry_func(e)):
                        raise
                    print(f"Attempt {attempt} failed. Retrying in {wait_time} seconds. Error: {str(e)}")
                    time.sleep(wait_time)
                    wait_time *= backoff_factor

        return wrapper

    return decorator
