"""Defines trends calculations for stations"""
import logging

import faust

from config import load_config, get_topic_prefix
from logging_factory import LoggerFactory

logger = LoggerFactory.get_logger(__name__)

config = load_config()
TOPIC_PREFIX = get_topic_prefix()
KAFKA_BROKER_URL = config['kafka']['broker']['url']

CONNECT_TOPIC_NAME = f"{TOPIC_PREFIX}.connect-stations"

# Faust will ingest records from Kafka in this format
class Station(faust.Record, serializer='json'):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool

    @property
    def line(self):
        if self.red and self.blue or self.red and self.green or self.blue and self.green:
            raise Exception("Station can have only 1 line while " + self)
        elif self.red:
            return "red"
        elif self.blue:
            return "blue"
        elif self.green:
            return "green"
        else:
            logging.warning("Cannot find line for station %s", self)


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


app = faust.App("stations-stream-4", broker=f"kafka://{KAFKA_BROKER_URL}", store="memory://")

topic = app.topic(CONNECT_TOPIC_NAME, value_type=Station)

out_topic = app.topic(f"{TOPIC_PREFIX}.stations.table.v1", partitions=1, value_type=TransformedStation)

# Table to map station-> line
table = app.Table(
    "transformed-stations",
    partitions=1,
    changelog_topic=out_topic,
)


@app.agent(topic)
async def station(stations):
    st: Station
    async for st in stations:
        station_id = str(st.station_id)
        try:
            _ = table[station_id]
        except KeyError:
            t = TransformedStation(station_id=st.station_id, station_name=st.station_name, order=st.order,
                                   line=st.line)
            if st.line is not None:
                logger.info("Record %s", t)
                table[station_id] = t


if __name__ == "__main__":
    app.main()
