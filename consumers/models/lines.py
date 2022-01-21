"""Contains functionality related to Lines"""
import json

from logging_factory import LoggerFactory
from models import Line

from config import get_topic_prefix

logger = LoggerFactory.get_logger(__name__)
TOPIC_PREFIX = get_topic_prefix()


class Lines:
    """Contains all train lines"""

    def __init__(self):
        """Creates the Lines object"""
        self.red_line = Line("red")
        self.green_line = Line("green")
        self.blue_line = Line("blue")

    def process_message(self, message):
        """Processes a station message"""
        logger.debug(f"processing message {message.value()} from topic {message.topic()}")
        if f"{TOPIC_PREFIX}.station" in message.topic():
            value = message.value()
            if message.topic() == f"{TOPIC_PREFIX}.stations.table.v1":
                value = json.loads(value)
            self.process_line_message(message, value["line"])
        elif "TURNSTILE_SUMMARY" == message.topic():
            logger.debug("Processing turnstile %s - %s", message.key(), message.value())
            key = json.loads(message.key())
            self.process_line_message(message, key['LINE'])
        else:
            logger.info("ignoring non-lines message %s", message.topic())

    def process_line_message(self, message, line):
        if line == "green":
            self.green_line.process_message(message)
        elif line == "red":
            self.red_line.process_message(message)
        elif line == "blue":
            self.blue_line.process_message(message)
        else:
            logger.debug("discarding unknown line msg %s", line)
