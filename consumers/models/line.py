"""Contains functionality related to Lines"""
import json
import logging.config
import os
from pathlib import Path

from models import Station

# Import logging before models to ensure configuration is picked up
path = f"{Path(__file__).parents[1]}/logging.ini"
assert os.path.exists(path), f"File not exists {path}"
logging.config.fileConfig(path)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        print(f"Station {value}")
        message = Station.from_message(value)
        self.stations[value["station_id"]] = message
        print(f"Station {message}")

    def _handle_arrival(self, message):
        """Updates train locations"""

        value = message.value()
        prev_station_id = value.get("prev_station_id")
        prev_dir = value.get("prev_direction")
        print(f"arrival from {prev_station_id} {prev_dir}")
        if prev_dir is not None and prev_station_id is not None:
            prev_station: Station = self.stations.get(prev_station_id)
            if prev_station is not None:
                prev_station.handle_departure(prev_dir)
            else:
                print(f"unable to handle previous station due to missing station {len(self.stations)}")
        else:
            print(
                f"unable to handle previous station due to missing previous info {len(self.stations)}"
            )
        print(1)
        station_id = value.get("station_id")
        print(2)
        station: Station = self.stations.get(station_id)
        print(3)
        if station is None:
            print("unable to handle message due to missing station")
            return
        print(f"Station handle arrival {station}. Value={value}")
        station.handle_arrival(
            value.get("direction"), value.get("train_id"), value.get("train_status")
        )
        print("Successfully handled station message")

    def process_message(self, message):
        """Given a kafka message, extract data"""

        # TODO: Based on the message topic, call the appropriate handler.
        print(f"Received message for line {message.topic()}. Value {message.value()}")
        # print(f"Logger level {logger.isEnabledFor(logging.INFO)}")

        if message.topic() == "org.chicago.cta.stations.table.v1":
            try:
                value = json.loads(message.value())
                self._handle_station(value)
            except Exception as e:
                logger.fatal("bad station? %s, %s", value, e)
        elif "org.chicago.cta.station" in message.topic():
            self._handle_arrival(message)
        elif "TURNSTILE_SUMMARY" == message.topic():
            json_data = json.loads(message.value())
            station_id = json_data.get("STATION_ID")
            station = self.stations.get(station_id)
            if station is None:
                logger.debug("unable to handle message due to missing station")
                return
            station.process_message(json_data)
        else:
            logger.debug(
                "unable to find handler for message from topic %s", message.topic
            )
