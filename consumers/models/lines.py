"""Contains functionality related to Lines"""
import json
import logging.config
import os
from pathlib import Path

from models import Line

path = f"{Path(__file__).parents[1]}/logging.ini"
assert os.path.exists(path), f"File not exists {path}"
logging.config.fileConfig(path)

logger = logging.getLogger(__name__)


class Lines:
    """Contains all train lines"""

    def __init__(self):
        """Creates the Lines object"""
        self.red_line = Line("red")
        self.green_line = Line("green")
        self.blue_line = Line("blue")

    def process_message(self, message):
        """Processes a station message"""
        print(f"processing message {message.value()} from topic {message.topic()}")
        if "org.chicago.cta.station" in message.topic():
            value = message.value()
            if message.topic() == "org.chicago.cta.stations.table.v1":
                value = json.loads(value)
            if value["line"] == "green":
                self.green_line.process_message(message)
            elif value["line"] == "red":
                self.red_line.process_message(message)
            elif value["line"] == "blue":
                self.blue_line.process_message(message)
            else:
                logger.debug("discarding unknown line msg %s", value["line"])
        elif "TURNSTILE_SUMMARY" == message.topic():
            print("Processing turnstile")
            self.green_line.process_message(message)
            self.red_line.process_message(message)
            self.blue_line.process_message(message)
        else:
            logger.info("ignoring non-lines message %s", message.topic())
