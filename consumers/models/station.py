"""Contains functionality related to Stations"""

from logging_factory import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


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
        logger.debug("Handle departure")
        if direction == "a":
            self.dir_a = None
        else:
            self.dir_b = None

    def handle_arrival(self, direction, train_id, train_status):
        """Unpacks arrival data"""
        status_dict = {"train_id": train_id, "status": train_status.replace("_", " ")}
        logger.info(f"Train arrived. {status_dict}")
        if direction == "a":
            self.dir_a = status_dict
        else:
            self.dir_b = status_dict

    def process_message(self, json_data):
        """Handles arrival and turnstile messages"""
        value = json_data["COUNT"]
        self.num_turnstile_entries = value

    def __str__(self) -> str:
        return f" Station( station_id={self.station_id},station_name={self.station_name},order={self.order},dir_a={self.dir_a}," \
               f"dir_b={self.dir_b}, num_turnstile_entries={self.num_turnstile_entries}"
