"""Producer base-class providing common utilites and functionality"""
import time

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

from config import load_config
from logging_factory import LoggerFactory

logger = LoggerFactory.get_logger(__name__)
config = load_config()


class Producer:
    """Defines and provides common functionality amongst Producers"""

    def __init__(
            self,
            topic_name,
            key_schema,
            value_schema=None,
            num_partitions=config['kafka']['broker']['topics']['creation']['num-partitions'],
            num_replicas=config['kafka']['broker']['topics']['creation']['num-replicas'],
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        self.broker_properties = {
            "schema.registry.url": config['kafka']['schema-registry']['url'],
            "bootstrap.servers": config['kafka']['bootstrap']['servers']
        }

        self.producer = AvroProducer(config=self.broker_properties, default_key_schema=self.key_schema,
                                     default_value_schema=self.value_schema)
        self.client = AdminClient({"bootstrap.servers": self.broker_properties.get("bootstrap.servers")})

        # If the topic does not already exist, try to create it
        if not self.topic_exists(self.topic_name):
            self.create_topic()

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        futures = self.client.create_topics(
            [
                NewTopic(
                    self.topic_name,
                    num_partitions=self.num_partitions,
                    replication_factor=self.num_replicas,
                )
            ]
        )

        for topic, future in futures.items():
            try:
                future.result()
                logger.info("topic %s created", self.topic_name)
            except Exception as e:
                logger.error("failed to create topic %s: %s", self.topic_name, e)
                # Ignore as a topic is already created
                # raise

    @staticmethod
    def time_millis():
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        self.producer.flush()

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))

    def topic_exists(self, topic):
        """Checks if the given topic exists in Kafka"""
        topic_metadata = self.client.list_topics(timeout=5)
        topics = topic_metadata.topics
        return topic in topics
