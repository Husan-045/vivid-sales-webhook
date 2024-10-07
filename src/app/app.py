import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from mangum import Mangum

from app.api.viagogo_webhook import router

logging.basicConfig(level=logging.INFO)

app = FastAPI()
lambda_handler = Mangum(app)
app.include_router(router)

# # Enable gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown_event():
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
