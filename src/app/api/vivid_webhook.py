import datetime
import os
import traceback
import urllib.parse
import uuid
from urllib.parse import urlparse

import boto3
import httpx
import psycopg2
import requests
from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, Request
from snowflake.connector.errors import ProgrammingError
from ticketboat_aws_utils.dynamodb_table import DynamodbTable

from app.service.s3_handler import upload_to_s3_for_snowflake
from app.service.secrets import get_secret
from app.service.snowflake import snowflake_cursor, get_description
from app.utils import dynamodb_resource



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
        request: Request
):
    vivid_account = request.query_params.get("vivid_account")
    print("account:", vivid_account)
    body = await request.body()
    print("Raw request body:", body)
    parsed_body = urllib.parse.parse_qs(body.decode('utf-8'))
    print(parsed_body)
    readable_body = {k: v[0] for k, v in parsed_body.items()}

    print(readable_body)

    id = str(uuid.uuid4().hex)
    print("storing in postgres")
    _upload_into_postgres(readable_body, vivid_account)
    print("confirm sale")
    confirm_sale(vivid_account, readable_body.get('orderid'))
    print("storing in s3")
    _store_in_s3(id, readable_body)
    print("storing in snowflake")
    _store_into_snowflake(id, readable_body, vivid_account)
    print("confirm sale")
    confirm_sale(vivid_account, readable_body.get('orderid'))
    print("redirecting to ticket_suit")
    await redirect_to_ticket_suit(body)
    print("monitor")
    CloudwatchMonitor().send_success_to_cloudwatch()
    print("success")
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
            "body": "{\"message\": \"Webhook received successfully\"}"
            }


async def redirect_to_ticket_suit(body):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://stubsai-api-live.azurewebsites.net/vividseats/order/9ee06c1d-b4dc-4b52-a501-eeba5de55bb5",
                content=body,  # Send the raw body
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",  # Set the correct Content-Type
                }
            )
            response.raise_for_status()  # Raise an error for non-2xx responses
        except httpx.RequestError as e:
            print(f"An error occurred while sending data to the target API: {e}")
            raise
        except httpx.HTTPStatusError as e:
            print(f"Target API returned an error: {e.response.status_code}, {e.response.text}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise


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


def _store_into_snowflake(id, readable_body, vivid_account):
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
                created_at,
                vivid_account 
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
                CURRENT_TIMESTAMP(),
                %(vivid_account)s
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
            'instant_flash_seats': readable_body.get('instantFlashSeats'),
            'vivid_account': vivid_account
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


def _upload_into_postgres(sale, vivid_account):
    _add_event_url_to_sale(sale)
    secrets = get_secret(f"{os.getenv('ENVIRONMENT')}/postgres/buylist/admin")
    print(secrets)
    conn = psycopg2.connect(
        dbname=secrets['dbname'],
        user=secrets['user'],
        password=secrets['password'],
        host=secrets['host'],
        port=secrets['port']
    )

    sale_tuple = (
        str(uuid.uuid4()), sale.get('orderid'), sale.get('ticketid'), vivid_account, sale.get('section'), sale.get('row'),
        sale.get('notes'), sale.get('quantity'), sale.get('total'), sale.get('event'), sale.get('date'),
        str(datetime.datetime.utcnow()), sale.get('venue'), 'UNCONFIRMED', sale.get('electronic'),
        sale.get('barCodesRequired'), sale.get('instantFlashSeats'), str(datetime.datetime.utcnow()), sale.get("event_url"))
    print("Uploading", sale)
    try:
        with conn.cursor() as cursor:
            insert_query = """
                    INSERT INTO vivid_sales (
                        id, order_id, broker_ticket_id, vivid_account_id, section, "row", notes, quantity, cost, event,
                        event_date, order_date, venue, status, electronic_delivery,  bar_codes_required,
                        instant_flash_seats, collection_session_ts, event_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (order_id)
                    DO NOTHING
                """
            cursor.execute(insert_query, sale_tuple)
        conn.commit()
    except Exception as e:
        traceback.print_exc()
        print(f"Error: {e}")
        raise
    finally:
        conn.close()
    pass

def _add_event_url_to_sale(sale):
    try:
        secrets = get_secret(f"{os.getenv('ENVIRONMENT')}/postgres/shadows-realtime-catalog-1-ro/dbadmin")
        print(secrets)
        conn = psycopg2.connect(
            dbname=secrets['dbname'],
            user=secrets['user'],
            password=secrets['password'],
            host=secrets['host'],
            port=secrets['port']
        )

        location_id = sale["brokerTicketId"].split(";")[0]
        print("location_id:", location_id)
        sale["event_url"] = _get_event_url(
            location_id,
            conn,
        )
    except Exception as e:
        print("Exception:", str(e))
        traceback.print_exc()
        sale["event_url"] = ""

def _get_event_url(
            location_id: str,
            pg_connection,
    ) -> str:
        try:
            event_code = _get_event_code(location_id, pg_connection)
            print("event_code:", event_code)
            if event_code:
                shadows_table = DynamodbTable(
                    dynamodb_resource,
                    "shadows-catalog",
                    automatically_append_env_to_table_name=True,
                )
                event_details = shadows_table.get_items_with_id_and_sub_id_prefix(
                    f"ticketmaster_event#{event_code}",
                    f"event_details", )
                if event_details:
                    return event_details[0].get("event_url", "")
                else:
                    print("Listing Not Found:")
                    return ""
            else:
                print("Event Code Not Found:")
            return ""
        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}")
            return ""

def _get_event_code(location_id: str, pg_connection):
        try:
            if location_id:
                query = """
                        SELECT event_code
                        FROM vivid_ticket_id_x_external_id
                        WHERE location_id = %s
                    """
                with pg_connection.cursor() as cursor:
                    cursor.execute(query, (location_id,))
                    result = cursor.fetchone()
                    return result[0] if result else None
            else:
                return ""
        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}")
            return ""