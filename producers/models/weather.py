"""Methods pertaining to weather data"""
import datetime
import json
import random
from enum import IntEnum
from pathlib import Path

import requests

from config import load_config, get_topic_prefix
from logging_factory import LoggerFactory
from models.producer import Producer

logger = LoggerFactory.get_logger(__name__)

config = load_config()
rest_proxy_config = config['kafka']['rest-proxy']

TOPIC_PREFIX = get_topic_prefix()


class Weather(Producer):
    """Defines a simulated weather model"""

    status = IntEnum(
        "status", "sunny partly_cloudy cloudy windy precipitation", start=0
    )

    rest_proxy_url = rest_proxy_config['url']

    key_schema = None
    value_schema = None

    winter_months = set((0, 1, 2, 3, 10, 11))
    summer_months = set((6, 7, 8))

    def __init__(self, month):
        if Weather.key_schema is None:
            with open(f"{Path(__file__).parents[0]}/schemas/weather_key.json") as f:
                Weather.key_schema = json.load(f)

        if Weather.value_schema is None:
            with open(f"{Path(__file__).parents[0]}/schemas/weather_value.json") as f:
                Weather.value_schema = json.load(f)

        super().__init__(
            f"{TOPIC_PREFIX}.weather.v1",
            key_schema=Weather.key_schema,
            value_schema=Weather.value_schema,
        )

        self.status = Weather.status.sunny
        self.temp = 70.0
        if month in Weather.winter_months:
            self.temp = 40.0
        elif month in Weather.summer_months:
            self.temp = 85.0



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
            "temperature": int(self.temp),
            "status": self.status.name
        }

        request = {
            "key_schema": json.dumps(Weather.key_schema),
            "value_schema": json.dumps(Weather.value_schema),
            "records": [
                {
                    "key": key,
                    "value": value
                }
            ]
        }
        request_string = json.dumps(request)
        logger.debug(f"Weather request {request_string}")
        resp = requests.post(
            f"{Weather.rest_proxy_url}/topics/{self.topic_name}",
            headers={"Content-Type": "application/vnd.kafka.avro.v2+json"},
            data=request_string,
        )
        try:
            resp.raise_for_status()
        except Exception as e:
            logger.error("Response %s", resp.json())
            raise e

        logger.info(
            "sent weather data to kafka topic %s, temp: %s, status: %s",
            self.topic_name,
            self.temp,
            self.status.name,
        )
