"""Contains functionality related to Lines"""
import json

from logging_factory import LoggerFactory
from models import Station

from config import get_topic_prefix

TOPIC_PREFIX = get_topic_prefix()

logger = LoggerFactory.get_logger(__name__)


class Line:
    """Defines the Line Model"""

    def __init__(self, color):
        """Creates a line"""
        self.color = color
        self.color_code = "0xFFFFFF"
        if self.color == "blue":
            self.color_code = "#1E90FF"
        elif self.color == "red":
            self.color_code = "#DC143C"
        elif self.color == "green":
            self.color_code = "#32CD32"
        self.stations = {}

    def _handle_station(self, value):
        """Adds the station to this Line's data model"""
        if value["line"] != self.color:
            return
        message = Station.from_message(value)
        self.stations[value["station_id"]] = message

    def _handle_arrival(self, message):
        """Updates train locations"""

        value = message.value()
        prev_station_id = value.get("prev_station_id")
        prev_dir = value.get("prev_direction")
        logger.info(f"arrival from  station {prev_station_id} and direction {prev_dir}")
        if prev_dir is not None and prev_station_id is not None:
            prev_station: Station = self.stations.get(prev_station_id)
            if prev_station is not None:
                prev_station.handle_departure(prev_dir)
            else:
                logger.info(f"unable to handle previous station due to missing station {len(self.stations)}")
        else:
            logger.info(
                f"unable to handle previous station due to missing previous info {len(self.stations)}"
            )
        station_id = value.get("station_id")
        station: Station = self.stations.get(station_id)
        if station is None:
            logger.info("unable to handle message due to missing station")
            return
        station.handle_arrival(
            value.get("direction"), value.get("train_id"), value.get("train_status")
        )

    def process_message(self, message):
        """Given a kafka message, extract data"""

        logger.debug(f"Received message for line {message.topic()}. Value {message.value()}")

        if message.topic() == f"{TOPIC_PREFIX}.stations.table.v1":
            try:
                value = json.loads(message.value())
                self._handle_station(value)
            except Exception as e:
                logger.fatal("bad station? %s, %s", value, e)
        elif f"{TOPIC_PREFIX}.station" in message.topic():
            self._handle_arrival(message)
        elif "TURNSTILE_SUMMARY" == message.topic():
            json_data = json.loads(message.value().decode('utf-8'))
            key = json.loads(message.key())
            logger.debug("Turnstile key %s", key)
            station_id = int(key['STATION_ID'])
            station: Station = self.stations.get(station_id)
            if station is None:
                logger.info(
                    f"unable to handle message due to missing station")
                return
            station.process_message(json_data)
        else:
            logger.debug(
                "unable to find handler for message from topic %s", message.topic
            )
