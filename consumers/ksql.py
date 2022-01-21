"""Configures KSQL to combine station and turnstile data"""
import json
import logging
import logging.config

import requests

import topic_check
from config import load_config, get_topic_prefix
from logging_factory import LoggerFactory

logger = LoggerFactory.get_logger(__name__)

config = load_config()
KSQL_URL = config['kafka']['ksql']['url']

KSQL_STATEMENT = f"""
CREATE STREAM turnstile (
    station_id BIGINT,
    station_name VARCHAR,
    line VARCHAR
) WITH (
    KAFKA_TOPIC = '{get_topic_prefix()}.turnstile',
    VALUE_FORMAT='AVRO'
);

CREATE TABLE TURNSTILE_SUMMARY  WITH (VALUE_FORMAT='JSON',
        KEY_FORMAT = 'JSON') AS SELECT
 station_id, line, COUNT(*) as count from turnstile GROUP BY station_id, line;
"""

TOPIC_NAME = "TURNSTILE_SUMMARY"


def execute_statement():
    """Executes the KSQL statement against the KSQL API"""
    if topic_check.topic_exists(TOPIC_NAME) is True:
        logger.info(f"Topic {TOPIC_NAME} already exists. Will skip query execution")
        return

    logging.info("executing ksql statement...")

    resp = requests.post(
        f"{KSQL_URL}/ksql",
        headers={"Content-Type": "application/vnd.ksql.v1+json"},
        data=json.dumps(
            {
                "ksql": KSQL_STATEMENT,
                "streamsProperties": {"ksql.streams.auto.offset.reset": "earliest"},
            }
        ),
    )

    # Ensure that a 2XX status code was returned
    try:
        resp.raise_for_status()
    except Exception as e:
        logger.error("Response %s", resp.json())
        raise e
    logger.info("Successfully executed queries")


if __name__ == "__main__":
    execute_statement()
