"""Creates a turnstile data producer"""
import datetime
import logging
from pathlib import Path

from confluent_kafka import avro
from models.producer import Producer
from models.turnstile_hardware import TurnstileHardware

from config import get_topic_prefix

logger = logging.getLogger(__name__)

TOPIC_PREFIX = get_topic_prefix()


class Turnstile(Producer):
    key_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/turnstile_key.json")

    value_schema = avro.load(
        f"{Path(__file__).parents[0]}/schemas/turnstile_value.json"
    )

    def __init__(self, station):
        """Create the Turnstile"""
        topic_name = f"{TOPIC_PREFIX}.turnstile"
        super().__init__(
            topic_name,
            key_schema=Turnstile.key_schema,
            value_schema=Turnstile.value_schema,
        )
        self.station = station
        self.turnstile_hardware = TurnstileHardware(station)

    def run(self, timestamp: datetime.datetime, time_step):
        """Simulates riders entering through the turnstile."""
        num_entries = self.turnstile_hardware.get_entries(timestamp, time_step)
        key = {
            "timestamp": timestamp.timestamp()
        }

        value = {
            "station_id": self.station.station_id,
            "station_name": self.station.name,
        }
        logger.debug(f"Station {self.station.station_id}. Turnstile entries {num_entries}")
        for _ in range(num_entries):
            logger.debug(f"Sending {key}={value} to topic {self.topic_name}")
            self.producer.produce(topic=self.topic_name, key=key, value=value)
