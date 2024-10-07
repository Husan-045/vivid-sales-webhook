import logging

from fastapi import APIRouter, status

router = APIRouter()


@router.get("/healthcheck", status_code=status.HTTP_200_OK)
async def healthcheck():

    logging.info("healthcheck")

    return {"healthcheck": "Everything is OK!"}
