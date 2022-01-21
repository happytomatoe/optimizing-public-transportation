"""Defines core consumer functionality"""

from confluent_kafka import Consumer, OFFSET_BEGINNING
from confluent_kafka.avro import AvroConsumer
from tornado import gen

from config import load_config
from logging_factory import LoggerFactory

logger = LoggerFactory.get_logger(__name__)
config = load_config()


class KafkaConsumer:
    """Defines the base kafka consumer class"""

    def __init__(
            self,
            topic_name_pattern,
            message_handler,
            is_avro=True,
            offset_earliest=False,
            sleep_secs=1.0,
            consume_timeout=0.1,
    ):
        """Creates a consumer object for asynchronous use"""
        self.topic_name_pattern = topic_name_pattern
        self.message_handler = message_handler
        self.sleep_secs = sleep_secs
        self.consume_timeout = consume_timeout
        self.offset_earliest = offset_earliest

        self.broker_properties = {
            "group.id": "org.chicago.cta.consumers",
            "bootstrap.servers": config['kafka']['bootstrap']['servers']
        }

        if is_avro is True:
            self.broker_properties["schema.registry.url"] = config['kafka']['schema-registry']['url']
            self.consumer = AvroConsumer(self.broker_properties)
        else:
            self.consumer = Consumer(self.broker_properties)
        logger.info("Subscribing to %s", topic_name_pattern)
        self.consumer.subscribe([topic_name_pattern], on_assign=self.on_assign)

    def on_assign(self, consumer, partitions):
        """Callback for when topic assignment takes place"""
        if self.offset_earliest:
            for partition in partitions:
                partition.offset = OFFSET_BEGINNING

        logger.info("partitions assigned for %s", self.topic_name_pattern)
        consumer.assign(partitions)

    async def consume(self):
        """Asynchronously consumes data from kafka topic"""
        logger.debug(f"Consuming from {self.topic_name_pattern}")

        while True:
            num_results = 1
            while num_results > 0:
                num_results = self._consume()
            await gen.sleep(self.sleep_secs)

    def _consume(self):
        """Polls for a message. Returns 1 if a message was received, 0 otherwise"""
        logger.debug("Polling from %s", self.topic_name_pattern)
        message = self.consumer.poll(self.consume_timeout)
        if message is None:
            logger.debug("No messages in %s", self.topic_name_pattern)
            return 0
        elif message.error():
            logger.error(f'Consumer error: {message.error().str()}')
            return 0
        else:
            logger.debug("Found message in %s", self.topic_name_pattern)
            self.message_handler(message)
            return 1

    def close(self):
        """Cleans up any open kafka consumers"""
        self.consumer.close()
