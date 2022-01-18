"""Methods pertaining to weather data"""
import base64
import datetime
import decimal
from ast import literal_eval
from enum import IntEnum
import json
import logging
from io import BytesIO
from pathlib import Path
import random
import urllib.parse

import fastavro
import requests
from confluent_kafka import avro

from models.producer import Producer

logger = logging.getLogger(__name__)


class Weather(Producer):
    """Defines a simulated weather model"""

    status = IntEnum(
        "status", "sunny partly_cloudy cloudy windy precipitation", start=0
    )

    rest_proxy_url = "http://localhost:8082"

    key_schema = None
    value_schema = None

    winter_months = set((0, 1, 2, 3, 10, 11))
    summer_months = set((6, 7, 8))

    def __init__(self, month):
        super().__init__(
            "weather",  # TODO: Come up with a better topic name
            key_schema=Weather.key_schema,
            value_schema=Weather.value_schema,
        )

        self.status = Weather.status.sunny
        self.temp = 70.0
        if month in Weather.winter_months:
            self.temp = 40.0
        elif month in Weather.summer_months:
            self.temp = 85.0

        if Weather.key_schema is None:
            with open(f"{Path(__file__).parents[0]}/schemas/weather_key.json") as f:
                Weather.key_schema = json.load(f)

        if Weather.value_schema is None:
            with open(f"{Path(__file__).parents[0]}/schemas/weather_value.json") as f:
                Weather.value_schema = json.load(f)

    def _set_weather(self, month):
        """Returns the current weather"""
        mode = 0.0
        if month in Weather.winter_months:
            mode = -1.0
        elif month in Weather.summer_months:
            mode = 1.0
        self.temp += min(max(-20.0, random.triangular(-10.0, 10.0, mode)), 100.0)
        self.status = random.choice(list(Weather.status))

    def run(self, curr_time: datetime.datetime):
        self._set_weather(curr_time.month)

        key = {
            "timestamp": curr_time.timestamp()
        }
        value = {
            "temperature": decimal.Decimal(str(self.temp)).quantize(decimal.Decimal('.1'),
                                                                    rounding=decimal.ROUND_DOWN),
            "status": self.status.name
        }

        request = {
            "key_schema": json.dumps(Weather.key_schema),
            "value_schema": json.dumps(Weather.value_schema),
            "records": [
                {
                    "key": key,
                    "value":  value
                }
            ]
        }
        request_string = json.dumps(request, ensure_ascii=False, default=str)
        logger.info(f"Request { request_string}")
        resp = requests.post(
            f"{Weather.rest_proxy_url}/topics/{self.topic_name}",
            headers={"Content-Type": "application/vnd.kafka.avro.v2+json"},
            data=request_string,
        )
        logger.info("response from server %s", resp.content)
        resp.raise_for_status()

        logger.debug(
            "sent weather data to kafka, temp: %s, status: %s",
            self.temp,
            self.status.name,
        )
