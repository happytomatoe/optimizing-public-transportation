"""Defines trends calculations for stations"""
import logging

import faust

from config import load_config, get_topic_prefix

logger = logging.getLogger(__name__)

config = load_config()
KAFKA_BROKER_URL = config['kafka']['broker']['url']


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
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


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


app = faust.App("stations-stream", broker=f"kafka://{KAFKA_BROKER_URL}", store="memory://")

topic = app.topic(f"{get_topic_prefix()}.connect-stations", value_type=Station)

out_topic = app.topic("connect-transformed-stations", partitions=1, value_type=TransformedStation)

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
            logger.info("Record %s", t)
            table[station_id] = t


if __name__ == "__main__":
    app.main()
