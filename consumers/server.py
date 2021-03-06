"""Defines a Tornado Server that consumes Kafka Event data for display"""
import logging
import logging.config
from pathlib import Path

import tornado.ioloop
import tornado.template
import tornado.web

import ksql
import topic_check
from config import get_topic_prefix

TOPIC_PREFIX = get_topic_prefix()
from consumer import KafkaConsumer
from logging_factory import LoggerFactory
from models import Lines, Weather

logger = LoggerFactory.get_logger(__name__)


class MainHandler(tornado.web.RequestHandler):
    """Defines a web request handler class"""

    template_dir = tornado.template.Loader(f"{Path(__file__).parents[0]}/templates")
    template = template_dir.load("status.html")

    def initialize(self, weather, lines):
        """Initializes the handler with required configuration"""
        self.weather = weather
        self.lines = lines

    def get(self):
        """Responds to get requests"""
        logging.debug("rendering and writing handler template")
        logging.debug("Weather %s", self.weather)

        self.write(
            MainHandler.template.generate(weather=self.weather, lines=self.lines)
        )


def run_server():
    """Runs the Tornado Server and begins Kafka consumption"""
    # Configure KSQL
    ksql.execute_statement()
    if topic_check.topic_exists("TURNSTILE_SUMMARY") is False:
        logger.fatal(
            "Ensure that the KSQL Command has run successfully before running the web server!"
        )
        exit(1)
    if topic_check.topic_exists(f"{TOPIC_PREFIX}.stations.table.v1") is False:
        logger.fatal(
            "Ensure that Faust Streaming is running successfully before running the web server!"
        )
        exit(1)

    weather_model = Weather()
    lines = Lines()

    application = tornado.web.Application(
        [(r"/", MainHandler, {"weather": weather_model, "lines": lines})]
    )
    application.listen(3000)

    # Build kafka consumers
    consumers = [
        KafkaConsumer(
            f"{TOPIC_PREFIX}.weather.v1",
            weather_model.process_message,
            offset_earliest=True,
        ),
        KafkaConsumer(
            f"{TOPIC_PREFIX}.stations.table.v1",
            lines.process_message,
            offset_earliest=True,
            is_avro=False,
        ),
        KafkaConsumer(
            f"^{TOPIC_PREFIX}.station.arrivals.",
            lines.process_message,
            offset_earliest=True,
        ),
        KafkaConsumer(
            "TURNSTILE_SUMMARY",
            lines.process_message,
            offset_earliest=True,
            is_avro=False,
        ),
    ]

    try:
        logger.info(
            "Click on the Preview button to see the Transit Status Page"
            "If running locally - Open a web browser to http://localhost:3000 to see the Transit Status Page"
        )
        for consumer in consumers:
            tornado.ioloop.IOLoop.current().spawn_callback(consumer.consume)

        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt as e:
        logger.info("shutting down server")
        tornado.ioloop.IOLoop.current().stop()
        for consumer in consumers:
            consumer.close()


if __name__ == "__main__":
    run_server()
