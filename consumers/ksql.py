"""Configures KSQL to combine station and turnstile data"""
import json
import logging
import logging.config
import os
from pathlib import Path

import requests

import topic_check
from config import load_config, get_topic_prefix

path = f"{Path(__file__).parents[0]}/logging.ini"
assert os.path.exists(path), f"File not exists {path}"
logging.config.fileConfig(path)

logger = logging.getLogger(__name__)

config = load_config()
KSQL_URL = config['kafka']['ksql']['url']
# TODO: number of turnstile entries is always increasing. It should probably decrease on some event

KSQL_STATEMENT = f"""
CREATE STREAM turnstile (
    station_id BIGINT,
    station_name VARCHAR
) WITH (
    KAFKA_TOPIC = '{get_topic_prefix()}.turnstile', 
    VALUE_FORMAT = 'AVRO'
);

CREATE TABLE turnstile_summary AS
    SELECT station_id, COUNT(*) as count FROM turnstile 
    GROUP BY station_id;
"""

TOPIC_NAME = "TURNSTILE_SUMMARY"


def execute_statement():
    """Executes the KSQL statement against the KSQL API"""
    # TODO: change as it'\s not idempotent
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
    resp.raise_for_status()
    logger.info("Successfully executed queries")


if __name__ == "__main__":
    execute_statement()
