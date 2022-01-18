CREATE STREAM stations (
    stop_id BIGINT,
    direction_id VARCHAR,
    stop_name VARCHAR,
    station_name VARCHAR,
    station_descriptive_name varchar,
    station_id BIGINT,
    order int,
    red boolean,
    blue boolean,
    green boolean
  ) WITH (
    KAFKA_TOPIC = 'connect-stations',
    VALUE_FORMAT = 'AVRO'
  );
