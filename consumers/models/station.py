"""Contains functionality related to Stations"""
import logging.config
import os
from pathlib import Path

path = f"{Path(__file__).parents[1]}/logging.ini"
assert os.path.exists(path), f"File not exists {path}"
logging.config.fileConfig(path)

logger = logging.getLogger(__name__)


class Station:
    """Defines the Station Model"""

    def __init__(self, station_id, station_name, order):
        """Creates a Station Model"""
        self.station_id = station_id
        self.station_name = station_name
        self.order = order
        self.dir_a = None
        self.dir_b = None
        self.num_turnstile_entries = 0

    @classmethod
    def from_message(cls, value):
        """Given a Kafka Station message, creates and returns a station"""
        return Station(value["station_id"], value["station_name"], value["order"])

    def handle_departure(self, direction):
        """Removes a train from the station"""
        print("Handle departure")
        if direction == "a":
            self.dir_a = None
        else:
            self.dir_b = None

    def handle_arrival(self, direction, train_id, train_status):
        """Unpacks arrival data"""
        print(f"arrival 1. Params {direction}\t{train_id}\t{train_status}")
        status_dict = {"train_id": train_id, "status": train_status.replace("_", " ")}
        print(f"Arrival to {direction}. Status dict {status_dict}")
        if direction == "a":
            self.dir_a = status_dict
        else:
            self.dir_b = status_dict

    def process_message(self, json_data):
        """Handles arrival and turnstile messages"""
        print("Setting count")
        self.num_turnstile_entries = json_data["COUNT"]

    def __str__(self) -> str:
        return f" Station( station_id={self.station_id},station_name={self.station_name},order={self.order},dir_a={self.dir_a}," \
               f"dir_b={self.dir_b}, num_turnstile_entries={self.num_turnstile_entries}"
