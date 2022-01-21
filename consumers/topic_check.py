from confluent_kafka.admin import AdminClient

from config import load_config

config = load_config()


def topic_exists(topic):
    """Checks if the given topic exists in Kafka"""
    client = AdminClient({"bootstrap.servers": config['kafka']['bootstrap']['servers']})
    topic_metadata = client.list_topics(timeout=5)
    topics = topic_metadata.topics
    return topic in topics
