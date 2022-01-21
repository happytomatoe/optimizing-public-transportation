"""Contains functionality related to Weather"""

import logging.config

logger = logging.getLogger(__name__)


class Weather:
    """Defines the Weather model"""

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 79.0
        self.status = "sunny"

    def process_message(self, message):
        """Handles incoming weather data"""
        value = message.value()
        logger.info("Incoming weather message %s", value)
        self.temperature = float(value['temperature'])
        self.status = value['status']

    def __str__(self) -> str:
        return f"Weather data. Temp={self.temperature}, status={self.status}"
