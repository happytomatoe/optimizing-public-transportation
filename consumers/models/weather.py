"""Contains functionality related to Weather"""
import logging

import logging.config
from pathlib import Path

# Import logging before models to ensure configuration is picked up
logging.config.fileConfig(f"{Path(__file__).parents[1]}/logging.ini")
logger = logging.getLogger(__name__)


class Weather:
    """Defines the Weather model"""

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 79.0
        self.status = "sunny"

    def process_message(self, message):
        """Handles incoming weather data"""
        logger.info("weather process_message is incomplete - skipping")
        logger.info(f"Weather {message}")
        #
        #
        # TODO: Process incoming weather messages. Set the temperature and status.
        #
        #
