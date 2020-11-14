from fastapi import APIRouter, Form, Response
from typing import List, Dict
from tortoise.queryset import QuerySet

from ..models.models import Covid19Cases, Message

from twilio.twiml.messaging_response import MessagingResponse

router = APIRouter()

valid_commands = ["CASES", "DEATHS"]


@router.post("/api/v1/")
async def Twilio_request_info(Body: str = Form(...)):
    """
    # To get request info from TWILIO API
    """
    # Extract the query message
    message = Body.strip().split(" ")

    # Validate and parse message to query db if the message is valid
    if len(message) > 2 or message[0] not in valid_commands:
        response = "Invalid message, Please provide a query in the form as mentioned in https://www.domain.com/docs/whatsapp/api#conversational-messaging-on-whatsapp"
    else:
        if message[0] == "CASES":
            column = "TotalActive"
            template = "Active Cases "
        elif message[0] == "DEATHS":
            column = "TotalDeaths"
            template = "Deaths "
        response = message[1] + " " + template
        if message[1] == "TOTAL":
            message[1] = "GLB"
            response = "Total" + " " + template
        # Query the DB, we could validate the list of countries before querying the DB by keeping a valid_country_codes list as well
        result = (
            await Covid19Cases.filter(CountryCode=message[1])
            .order_by("-FetchedDate")
            .limit(1)
            .only(column)
            .values(column)
        )
        if not result:
            response = "Invalid Country code provided, Please provide a country code from the list in https://www.domain.com/docs/whatsapp/api#conversational-messaging-on-whatsapp-countries-list"
        else:
            response = response + str(result[0][column])
    # Prepare response in TWILIO's accepted form
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(response)
    # Return the response
    return Response(content=str(resp), media_type="application/xml")


# @router.post("/api/v1/testdb/")
# async def DB_queries(body: Message):
#     """
#     # To get request info from TWILIO API
#     """
#     message = body.message.strip().split(" ")
#     column = message[0]
#     result = (
#         await Covid19Cases.filter(CountryCode=message[1])
#         .order_by("-FetchedDate")
#         .only(column)
#         .values(column)
#     )
#     return result
