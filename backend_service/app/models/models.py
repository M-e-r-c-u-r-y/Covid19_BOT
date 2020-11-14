# pylint: disable=E0611, E0213
# https://github.com/samuelcolvin/pydantic/issues/568
from tortoise import fields
from tortoise.models import Model

from pydantic import BaseModel, ValidationError, validator


class Covid19Cases(Model):
    """
    The Covid19Cases Data Model
    """

    id = fields.IntField(pk=True)
    Country = fields.CharField(max_length=255)
    CountryCode = fields.CharField(max_length=4)
    FetchedDate = fields.DatetimeField()
    NewConfirmed = fields.IntField()
    NewDeaths = fields.IntField()
    NewRecovered = fields.IntField()
    TotalConfirmed = fields.IntField()
    TotalDeaths = fields.IntField()
    TotalRecovered = fields.IntField()
    TotalActive = fields.IntField(gt=0)

    class Meta:
        table = "Covid19Cases"

    def __str__(self):
        return self.name


class Message(BaseModel):
    """
    The data model for the messages we get from the TWILIO API
    """

    message: str