"""Configures a Kafka Connector for Postgres Station data"""
import json
import logging

import requests
import yaml

from config import get_topic_prefix

logger = logging.getLogger(__name__)

config = yaml.safe_load(open("config.yml"))
connect_config = config['kafka']['connect']
KAFKA_CONNECT_URL = connect_config['url']
CONNECTOR_NAME = "stations"


def configure_connector():
    """Starts and configures the Kafka Connect connector"""
    logging.info("creating or updating kafka connect connector...")
    connectors_url = f"{KAFKA_CONNECT_URL}/connectors"

    resp = requests.get(f"{connectors_url}/{CONNECTOR_NAME}")
    if resp.status_code == 200:
        logging.info("connector already created skipping recreation")
        return

    resp = requests.post(
        connectors_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "name": CONNECTOR_NAME,
                "config": {
                    "name": "stations",
                    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
                    "connection.url": "jdbc:postgresql://postgres:5432/cta",
                    "connection.user": "cta_admin",
                    "connection.password": "chicago",
                    "table.whitelist": "stations",
                    "dialect.name": "PostgreSqlDatabaseDialect",
                    "mode": "incrementing",
                    "incrementing.column.name": "stop_id",
                    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "value.converter.schemas.enable": "false",
                    "topic.prefix": f"{get_topic_prefix()}.connect-",
                    "batch.max.rows": "500",
                }
            }),
    )

    ## Ensure a healthy response was given
    resp.raise_for_status()
    logging.info("connector created successfully")


if __name__ == "__main__":
    if connect_config['enabled']:
        configure_connector()
    else:
        logger.info("kafka connect functionality is disabled")
