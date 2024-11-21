import os
import traceback
import urllib.parse
import uuid
from typing import Any

import boto3
import requests
from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, Request
from snowflake.connector.errors import ProgrammingError

from app.service.s3_handler import upload_to_s3_for_snowflake
from app.service.secrets import get_secret
from app.service.snowflake import snowflake_cursor, get_description

router = APIRouter()


class CloudwatchMonitor:
    def __init__(self, cloudwatch=boto3.client("cloudwatch")):
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


@router.post("/webhook")
async def vivid_webhook(
        request: Request, e: Any = None
):
    print("account:", e)
    body = await request.body()
    print("Raw request body:", body)

    # parsed_body = urllib.parse.parse_qs(payload.decode('utf-8'))
    # print(parsed_body)
    # readable_body = {k: v[0] for k, v in parsed_body.items()}
    #
    # print(readable_body)
    #
    # id = str(uuid.uuid4().hex)
    # _store_in_s3(id, readable_body)
    # _store_into_snowflake(id, readable_body)
    # confirm_sale(e, readable_body.get('orderid'))
    # CloudwatchMonitor().send_success_to_cloudwatch()
    print("success")
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
            "body": "{\"message\": \"Webhook received successfully\"}"
            }


def _store_in_s3(id, readable_body):
    order_id = readable_body.get('orderid')
    quantity = readable_body.get('quantity')
    ticket_id = readable_body.get('ticketid')
    total = readable_body.get('total')
    section = readable_body.get('section')
    row = readable_body.get('row')
    event = readable_body.get('event')
    venue = readable_body.get('venue')
    date = readable_body.get('date')
    bar_codes_required = readable_body.get('barCodesRequired')
    in_hand_date = readable_body.get('inHandDate')
    instant_download = readable_body.get('instantDownload')
    electronic = readable_body.get('electronic')
    instant_flash_seats = readable_body.get('instantFlashSeats')
    data = (
        id,
        order_id,
        quantity,
        ticket_id,
        total,
        section,
        row,
        event,
        venue,
        date,
        bar_codes_required,
        in_hand_date,
        instant_download,
        electronic,
        instant_flash_seats
    )
    csv_str = ','.join(str(x) for x in data)
    print(csv_str)
    upload_to_s3_for_snowflake('vivid_webhook', csv_str)


def _store_into_snowflake(id, readable_body):
    secrets = get_secret('prod/snowflake')['snowflake_credentials']
    cursor = snowflake_cursor(secrets)
    try:
        cursor.execute('''
            insert into vivid_sales_webhook (
                id,
                order_id,
                quantity,
                ticket_id,
                total,
                section,
                "row",
                event,
                venue,
                event_date,
                bar_codes_required,
                in_hand_date,
                instant_download,
                electronic,
                instant_flash_seats,
                created_at
            ) values (
                %(id)s,
                %(order_id)s,
                %(quantity)s,
                %(ticket_id)s,
                %(total)s,
                %(section)s,
                %(row)s,
                %(event)s,
                %(venue)s,
                %(date)s,
                %(bar_codes_required)s,
                %(in_hand_date)s,
                %(instant_download)s,
                %(electronic)s,
                %(instant_flash_seats)s,
                CURRENT_TIMESTAMP()
            )
        ''', {
            'id': id,
            'order_id': readable_body.get('orderid'),
            'quantity': readable_body.get('quantity'),
            'ticket_id': readable_body.get('ticketid'),
            'total': readable_body.get('total'),
            'section': readable_body.get('section'),
            'row': readable_body.get('row'),
            'event': readable_body.get('event'),
            'venue': readable_body.get('venue'),
            'date': readable_body.get('date'),
            'bar_codes_required': readable_body.get('barCodesRequired'),
            'in_hand_date': readable_body.get('inHandDate'),
            'instant_download': readable_body.get('instantDownload'),
            'electronic': readable_body.get('electronic'),
            'instant_flash_seats': readable_body.get('instantFlashSeats')
        })

        result = cursor.fetchone()
        print(get_description(cursor), result)
    except ProgrammingError as e:
        raise e
    finally:
        cursor.close()


def confirm_sale(account_id, order_id):
    account = get_account(account_id)
    if account:
        token = account.get('vivid_account_access_token')
        url = "https://brokers.vividseats.com/webservices/v1/confirmOrder"

        headers = {
            "Accept": "application/xml",
            "Content-Type": "*/*",
        }

        data = {
            "apiToken": token,
            "orderId": order_id,
            "shipNow": False
        }
        try:
            print("CONFIRMING", data)
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
        except Exception as e:
            print(f"Error confirming order: {e}")
            traceback.print_exc()


def get_account(account_id):
    dynamodb_resource = boto3.resource("dynamodb")
    table = dynamodb_resource.Table("shadows-catalog-prod")
    response = table.query(
        KeyConditionExpression=Key("id").eq("vivid_account")
                               & Key("sub_id").eq(f"vivid_account_id#{account_id}/")
    )
    items = response.get("Items", [])
    return items[0] if items else None


print(get_account("VS1shadows@gmail.com"))
