from api_poller.celery import app
from celery.utils.log import get_task_logger

import requests

from tortoise.models import Model
from tortoise import Tortoise, fields, run_async
from datetime import datetime

import os

DEFAULT = "Not Set"
DSN = os.environ.get("TORTOISEORM_DSN", DEFAULT)
POLLED_URL = os.environ.get("POLLED_URL", DEFAULT)

logger = get_task_logger(__name__)


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

    ########################################################################################################################################################
    # Decided against using Pydantic to compute during request processing and instead store the computed value directly after fetching
    ########################################################################################################################################################
    # Active cases would be Confirmed cases - (Deaths cases + Recovered cases): Computed in Totals context
    # def TotalActive(self) -> int:
    #     return int(self.TotalConfirmed - (self.TotalDeaths + self.TotalRecovered))
    #
    # class PydanticMeta:
    #     computed = ("TotalActive")


async def save_to_db(normalized_result=None, last_fetch_date=None):
    await Tortoise.init(db_url=DSN, modules={"models": ["api_poller.tasks"]})
    # Ideally should only run once so that the schema gets generated
    await Tortoise.generate_schemas()
    logger.info(f"Checking if {last_fetch_date} already in db")
    already_in_db = bool(
        await Covid19Cases.filter(
            CountryCode="GLB", FetchedDate=last_fetch_date
        ).count()
    )
    if not already_in_db:
        logger.info("Saving to DB ...")
        await Covid19Cases.bulk_create(normalized_result)
        logger.info("Saving to DB Successful")
    else:
        logger.info(
            f"Entries for {last_fetch_date} already present in db, skipping saving"
        )


@app.task
def poller():
    r = requests.get(POLLED_URL)
    if r.status_code == requests.codes.ok:
        data = r.json()
        logger.info("Fetch from external API successful")
        normalized_data = []
        normalized_data.append(data["Global"])
        normalized_data[0]["Country"] = "Global"
        normalized_data[0]["CountryCode"] = "GLB"
        interested_keys = {}
        for key in normalized_data[0].keys():
            interested_keys[key] = key
        # Changing the column name from reserved postgresql keyword Date
        interested_keys["Date"] = "FetchedDate"
        # Converting datetime to a format the tortoise-orm accepts
        normalized_data[0]["FetchedDate"] = datetime.strptime(
            data["Date"], "%Y-%m-%dT%H:%M:%SZ"
        )
        # Calculating active cases
        normalized_data[0]["TotalActive"] = normalized_data[0]["TotalConfirmed"] - (
            normalized_data[0]["TotalDeaths"] + normalized_data[0]["TotalRecovered"]
        )
        for country in data["Countries"]:
            new_item = {}
            for key, value in interested_keys.items():
                new_item[value] = country[key]
            new_item["TotalActive"] = new_item["TotalConfirmed"] - (
                new_item["TotalDeaths"] + new_item["TotalRecovered"]
            )
            new_item["FetchedDate"] = datetime.strptime(
                new_item["FetchedDate"], "%Y-%m-%dT%H:%M:%SZ"
            )
            normalized_data.append(new_item)

        normalized_result = map(lambda item: Covid19Cases(**item), normalized_data)
        run_async(save_to_db(normalized_result, normalized_data[0]["FetchedDate"]))
    else:
        logger.info("Fetch from external API failed")
