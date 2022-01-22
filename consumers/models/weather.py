"""Contains functionality related to Weather"""

from logging_factory import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class Weather:
    """Defines the Weather model"""

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 79.0
        self.status = "sunny"

    def process_message(self, message):
        """Handles incoming weather data"""
        value = message.value()
        logger.debug("Incoming weather message %s", value)
        self.temperature = value['temperature']
        self.status = value['status']
        logger.info("Weather %s", self)
        logger.info("Weather temp type", type(self.temperature))

    def __str__(self) -> str:
        return f"Weather data. Temp={self.temperature}, status={self.status}"
