import json
import uuid
from typing import Any

from app.aws.cloudwatch_monitor import get_cloudwatch_monitor
from app.models.models import *
from app.service.s3_handler import upload_to_s3_for_snowflake
from app.service.secrets import get_secret
from app.service.snowflake import snowflake_cursor, get_description
from fastapi import APIRouter, Body, Depends
from snowflake.connector.errors import ProgrammingError

router = APIRouter()


@router.post("/webhook")
def vivid_webhook(
        payload: Any = Body(None), cloudwatch_monitor=Depends(get_cloudwatch_monitor)
):
    print(payload)
    print(type(payload))

    payload_body = payload.get('body')
    account_id = payload.get('queryStringParameters').get('account_id')
    exchange = payload.get('queryStringParameters').get('exchange')

    print(account_id)
    print(exchange)
    print(payload_body)
    print(type(payload_body))
    json_data = json.loads(payload_body)
    print(json_data)
    print(type(json_data))

    webhook_payload = Webhook(**json_data)
    webhook_payload_embedded = json_data['_embedded']
    venue_payload_embedded = json_data['_embedded']['venue']['_embedded']

    print(webhook_payload)
    print(webhook_payload_embedded)
    print(venue_payload_embedded)

    event_payload = EventEmbedded(**webhook_payload_embedded)
    venue_embedded = VenueEmbedded(**venue_payload_embedded)

    id = str(uuid.uuid4().hex)
    topic = webhook_payload.topic
    action = webhook_payload.action
    event_id = event_payload.event.id
    event_name = event_payload.event.name
    start_date = event_payload.event.start_date
    on_sale_date = event_payload.event.on_sale_date
    sale_id = event_payload.sale.id
    sale_created_at = event_payload.sale.created_at
    sale_section = event_payload.sale.seating.section
    sale_row = event_payload.sale.seating.row
    sale_seat_from = event_payload.sale.seating.seat_from
    sale_seat_to = event_payload.sale.seating.seat_to
    sale_amount = event_payload.sale.proceeds.amount
    sale_currency_code = event_payload.sale.proceeds.currency_code
    sale_number_of_tickets = event_payload.sale.number_of_tickets
    sellerlisting_id = event_payload.seller_listing.id
    external_id = event_payload.seller_listing.external_id
    sellerlisting_created_at = event_payload.seller_listing.created_at
    sellerlisting_number_of_tickets = event_payload.seller_listing.number_of_tickets
    sellerlisting_section = event_payload.seller_listing.seating.section
    sellerlisting_row = event_payload.seller_listing.seating.row
    sellerlisting_seat_from = event_payload.seller_listing.seating.seat_from
    sellerlisting_seat_to = event_payload.seller_listing.seating.seat_to
    sellerlisting_amount = event_payload.seller_listing.ticket_price.amount
    sellerlisting_currency_code = event_payload.seller_listing.ticket_price.currency_code
    venue_id = event_payload.venue.id
    venue_name = event_payload.venue.name
    venue_city = event_payload.venue.city
    venue_country = venue_embedded.country.code

    data = (
        id,
        topic,
        action,
        event_id,
        event_name,
        start_date,
        on_sale_date,
        sale_id,
        sale_created_at,
        sale_section,
        sale_row,
        sale_seat_from,
        sale_seat_to,
        sale_amount,
        sale_currency_code,
        sale_number_of_tickets,
        sellerlisting_id,
        external_id,
        sellerlisting_created_at,
        sellerlisting_number_of_tickets,
        sellerlisting_section,
        sellerlisting_row,
        sellerlisting_seat_from,
        sellerlisting_seat_to,
        sellerlisting_amount,
        sellerlisting_currency_code,
        venue_id,
        venue_name,
        venue_city,
        venue_country,
        account_id,
        exchange
    )

    csv_str = ','.join(str(x) for x in data)

    print(csv_str)
    upload_to_s3_for_snowflake('vivid_webhook', csv_str)

    secrets = get_secret('prod/snowflake')['snowflake_credentials']
    cursor = snowflake_cursor(secrets)
    try:
        cursor.execute('''
            insert into vivid_webhook (
                id,
                topic,
                action,
                event_id,
                event_name,
                start_date,
                on_sale_date,
                sale_id,
                sale_created_at,
                sale_section,
                sale_row,
                sale_seat_from,
                sale_seat_to,
                sale_amount,
                sale_currency_code,
                sale_number_of_tickets,
                sellerlisting_id,
                external_id,
                sellerlisting_created_at,
                sellerlisting_number_of_tickets,
                sellerlisting_section,
                sellerlisting_row,
                sellerlisting_seat_from,
                sellerlisting_seat_to,
                sellerlisting_amount,
                sellerlisting_currency_code,
                venue_id,
                venue_name,
                venue_city,
                venue_country,
                account_id,
                exchange
            ) values (
                %(id)s,
                %(topic)s,
                %(action)s,
                %(event_id)s,
                %(event_name)s,
                %(start_date)s,
                %(on_sale_date)s,
                %(sale_id)s,
                %(sale_created_at)s,
                %(sale_section)s,
                %(sale_row)s,
                %(sale_seat_from)s,
                %(sale_seat_to)s,
                %(sale_amount)s,
                %(sale_currency_code)s,
                %(sale_number_of_tickets)s,
                %(sellerlisting_id)s,
                %(external_id)s,
                %(sellerlisting_created_at)s,
                %(sellerlisting_number_of_tickets)s,
                %(sellerlisting_section)s,
                %(sellerlisting_row)s,
                %(sellerlisting_seat_from)s,
                %(sellerlisting_seat_to)s,
                %(sellerlisting_amount)s,
                %(sellerlisting_currency_code)s,
                %(venue_id)s,
                %(venue_name)s,
                %(venue_city)s,
                %(venue_country)s,
                %(account_id)s,
                %(exchange)s
            )
        ''', {
            'id': id,
            'topic': topic,
            'action': action,
            'event_id': event_id,
            'event_name': event_name,
            'start_date': start_date,
            'on_sale_date': on_sale_date,
            'sale_id': sale_id,
            'sale_created_at': sale_created_at,
            'sale_section': sale_section,
            'sale_row': sale_row,
            'sale_seat_from': sale_seat_from,
            'sale_seat_to': sale_seat_to,
            'sale_amount': sale_amount,
            'sale_currency_code': sale_currency_code,
            'sale_number_of_tickets': sale_number_of_tickets,
            'sellerlisting_id': sellerlisting_id,
            'external_id': external_id,
            'sellerlisting_created_at': sellerlisting_created_at,
            'sellerlisting_number_of_tickets': sellerlisting_number_of_tickets,
            'sellerlisting_section': sellerlisting_section,
            'sellerlisting_row': sellerlisting_row,
            'sellerlisting_seat_from': sellerlisting_seat_from,
            'sellerlisting_seat_to': sellerlisting_seat_to,
            'sellerlisting_amount': sellerlisting_amount,
            'sellerlisting_currency_code': sellerlisting_currency_code,
            'venue_id': venue_id,
            'venue_name': venue_name,
            'venue_city': venue_city,
            'venue_country': venue_country,
            'account_id': account_id,
            'exchange': exchange
        })

        result = cursor.fetchone()
        print(get_description(cursor), result)
    except ProgrammingError as e:
        raise e
    finally:
        cursor.close()

    # cloudwatch_monitor.send_success_to_cloudwatch()
