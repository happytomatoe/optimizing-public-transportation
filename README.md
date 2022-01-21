# Public Transit Status with Apache Kafka

In this project, you will construct a streaming event pipeline around Apache Kafka and its ecosystem. Using public data from the [Chicago Transit Authority](https://www.transitchicago.com/data/) we will construct an event pipeline around Kafka that allows us to simulate and display the status of train lines in real time.

When the project is complete, you will be able to monitor a website to watch trains move from station to station.

![Final User Interface](images/ui.png)


## Prerequisites

The following are required to complete this project:

* Docker
* Python 3.7
* Access to a computer with a minimum of 16gb+ RAM and a 4-core CPU to execute the simulation

## Description

The Chicago Transit Authority (CTA) has asked us to develop a dashboard displaying system status for its commuters. We have decided to use Kafka and ecosystem tools like REST Proxy and Kafka Connect to accomplish this task.

Our architecture will look like so:

![Project Architecture](images/diagram.png)


### Documentation
In addition to the course content you have already reviewed, you may find the following examples and documentation helpful in completing this assignment:

* [Confluent Python Client Documentation](https://docs.confluent.io/current/clients/confluent-kafka-python/#)
* [Confluent Python Client Usage and Examples](https://github.com/confluentinc/confluent-kafka-python#usage)
* [REST Proxy API Reference](https://docs.confluent.io/current/kafka-rest/api.html#post--topics-(string-topic_name))
* [Kafka Connect JDBC Source Connector Configuration Options](https://docs.confluent.io/current/connect/kafka-connect-jdbc/source-connector/source_config_options.html)

## Directory Layout
The project consists of two main directories, `producers` and `consumers`.

The following directory layout indicates the files that the student is responsible for modifying by adding a `*` indicator. Instructions for what is required are present as comments in each file.

```
* - Indicates that the student must complete the code in this file

├── consumers
│   ├── consumer.py *
│   ├── faust_stream.py *
│   ├── ksql.py *
│   ├── models
│   │   ├── lines.py
│   │   ├── line.py *
│   │   ├── station.py *
│   │   └── weather.py *
│   ├── requirements.txt
│   ├── server.py
│   ├── topic_check.py
│   └── templates
│       └── status.html
└── producers
    ├── connector.py *
    ├── models
    │   ├── line.py
    │   ├── producer.py *
    │   ├── schemas
    │   │   ├── arrival_key.json
    │   │   ├── arrival_value.json *
    │   │   ├── turnstile_key.json
    │   │   ├── turnstile_value.json *
    │   │   ├── weather_key.json
    │   │   └── weather_value.json *
    │   ├── station.py *
    │   ├── train.py
    │   ├── turnstile.py *
    │   ├── turnstile_hardware.py
    │   └── weather.py *
    ├── requirements.txt
    └── simulation.py
```

## Running and Testing

To run the simulation, you must first start up the Kafka ecosystem on their machine utilizing Docker Compose.

```%> docker-compose up```

Docker compose will take a 3-5 minutes to start, depending on your hardware. Please be patient and wait for the docker-compose logs to slow down or stop before beginning the simulation.

Once docker-compose is ready, the following services will be available:

| Service                    | Host URL                                         | Docker URL                                           | Username | Password |
|----------------------------|--------------------------------------------------|------------------------------------------------------| --- | --- |
| Kafka Control center(UI)   | [http://localhost:9021](http://localhost:9021)   | http://topics-ui:8085                                |
| Kafka                      | PLAINTEXT://localhost:9092                       | PLAINTEXT://broker:29092                             |
| REST Proxy                 | [http://localhost:8082](http://localhost:8082/)  | http://rest-proxy:8082/                              |
| Schema Registry            | [http://localhost:8081](http://localhost:8081/ ) | http://schema-registry:8081/                         |
| Kafka Connect              | [http://localhost:8083](http://localhost:8083)   | http://connect:8083                                  |
| KSQL                       | [http://localhost:8088](http://localhost:8088)   | http://ksqldb-server:8088                            |
| PostgreSQL                 | `jdbc:postgresql://localhost:5432/cta`           | `jdbc:postgresql://postgres:5432/cta`                | `cta_admin` | `chicago` |

If you want to change configuration you can do so in [config.yml](config.yml)

### Running the Simulation

There are two pieces to the simulation, the `producer` and `consumer`

#### To run the `producer`:

`make producer`

#### To run the Faust Stream Processing Application:
`make faust`

#### To run the `consumer`:
`make consumer`

Once the server is running, you may hit `Ctrl+C` at any time to exit.
