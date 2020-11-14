from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
import os

from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from tortoise.queryset import QuerySet
from tortoise import Tortoise

from .routers import general

app = FastAPI(
    title="Covid19 project",
    description="This is a service to provide covid19 data polled from postman API to Whatsapp bot using TWILIO api",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the data from environment variables
DEFAULT = "Not Set"
DSN = os.environ.get("TORTOISEORM_DSN", DEFAULT)

# Check if api's working
@app.get("/", status_code=200)
def read_root_get():
    """
    # To check if API is working
    """
    return {"API": "Working"}


app.include_router(general.router, tags=["general"])


register_tortoise(
    app,
    db_url=DSN,
    modules={"models": ["app.models.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)