from pydantic import BaseModel
from typing import Optional

class Country(BaseModel):
    code: str
    name: str

class VenueEmbedded(BaseModel):
    country: Country

class Seating(BaseModel):
    section: str
    row: Optional[str] = ''
    seat_from: str
    seat_to: str

class TicketPrice(BaseModel):
    amount: float
    currency_code: str
    display: str

class Sale(BaseModel):
    id: int
    created_at: str
    seating: Seating
    proceeds: TicketPrice
    number_of_tickets: int

class Event(BaseModel):
    id: int
    name: str
    start_date: str
    on_sale_date: str

class SellerListing(BaseModel):
    id: int
    external_id: str
    created_at: str
    number_of_tickets: int
    seating: Seating
    ticket_price: TicketPrice

class Venue(BaseModel):
    id: int
    name: str
    city: str

class EventEmbedded(BaseModel):
    event: Event
    sale: Sale
    seller_listing: SellerListing
    venue: Venue

class Webhook(BaseModel):
    topic: str
    action: str