import asyncio
import atexit
import logging

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from mangum import Mangum

from app.api import (
    healthcheck_api, vivid_webhook
)

load_dotenv()

auth_excluded_routes = {
    "/healthcheck": "GET",
    "/webhook": "POST",
    "/docs": "GET",
    "/openapi.json": "GET",
    "/users/bootstrap": "GET",
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Include your routers
app.include_router(healthcheck_api.router)
app.include_router(vivid_webhook.router)

# Enable CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Enable gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.middleware("http")
async def check_authorization_header(request: Request, call_next):
    return await call_next(request)


# Singleton pattern to manage the event loop
class LoopSingleton:
    _loop = None

    @classmethod
    def get_event_loop(cls):
        if cls._loop is None:
            cls._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._loop)
        return cls._loop


# Initialize the database connection
loop = LoopSingleton.get_event_loop()


# Register the database close function to be called on shutdown
def cleanup():
    loop = LoopSingleton.get_event_loop()


atexit.register(cleanup)

# Mangum handler with lifespan="off"
lambda_handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
