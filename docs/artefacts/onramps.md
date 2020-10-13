# Onramps

Specify how Tremor connects to the outside world in order to receive from external systems.

All Onramps support circuit breakers as in that no new events are read from it in the case of a
circuit breaker triggering.

For example, the Kafka onramp receives data from a Kafka cluster by creating a local record
consumer, connecting to a set of topics and ingesting Kafka record data.

All onramps are of the form:

```yaml
onramp:
  - id: <unique onramp id>
    type: <onramp name>
    preprocessors: # can be omitted
      - <preprocessor 1>
      - <preprocessor 2>
      - ...
    codec: <codec of the data>
    config:
      <key>: <value>
```

The [`codec`](codecs.md) field is optional and if not provided will use onramps default codec.

The `config` contains a map (key-value pairs) specific to the onramp type.

## Delivery Properties

Onramps are able to act upon both circuit breaker from the downstream pipelines. Those are triggered when event delivery is acknowledged or when event delivery fails. Also when some part (offramps, operators) signals itself being broken, the circuit breaker opens, or when the downstream system heals, the circuit breaker closes again, signalling it is safe to send further events. How each onramp reacts, is described in the table below:

The column `Delivery Acknowledgements` describes when the onramp considers and reports the event delivered to the upstream it is connected to.

Onramp     | Delivery Acknowledgements                                           |
-----------|---------------------------------------------------------------------|
kafka      | always, only on `ack` event if `enable.auto.commit` is set to false |
udp        | not supported                                                       |
tcp        | not supported                                                       |
file       | not supported                                                       |
blaster    | not supported                                                       |
metronome  | not supported                                                       |
crononome  | not supported                                                       |
rest       | not supported                                                       |
PostgreSQL | not supported                                                       |
ws         | not supported                                                       |


## Supported Onramps

### kafka

The Kafka onramp connects to one or more Kafka topics. It uses librdkafka to handle connections and can use the full set of [librdkaka configuration options](https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md).

The default [codec](codecs.md#json) is `json`.

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-kafka://<config_first_broker_host>[:<config_first_broker_port>]/<topic>/<partition>/<offset>
```

Supported configuration options are:

- `group_id` - The Kafka consumer group id to use.
- `topics` - A list of topics to subscribe to.
- `brokers` - Broker servers to connect to. (Kafka nodes)
- `rdkafka_options` - A optional map of an option to value, where both sides need to be strings.

Example:

```yaml
onramp:
  - id: kafka-in
    type: kafka
    codec: json
    config:
      brokers:
        - kafka:9092
      topics:
        - demo
        - snotbadger
      group_id: demo
```

### udp

The UDP onramp allows receiving data via UDP datagrams.

The default [codec](codecs.md#string) is `string`.

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-udp://<sender_ip>:<sender_port>/<config_receive_port>
```

Supported configuration options are:

- `host` - The IP to listen on
- `port` - The Port to listen on

Example:

```yaml
onramp:
  - id: udp
    type: udp
    preprocessors:
      - decompress
      - gelf-chunking
      - decompress
    codec: json
    config:
      port: 12201
      host: "127.0.0.1"
```

### file

The file onramp reads the content of a file, line by line. And sends each line as an event. It has the ability to shut down the system upon completion. Files can be `xz` compressed.

The default [codec](codecs.md#json) is `json`.

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-file://<tremor-host.local>/<config_source_file>
```

Supported configuration options are:

- `source` - The file to read from.
- `close_on_done` - Terminates tremor once the file is processed.

Example:

```yaml
onramp:
  - id: in
    type: file
    config:
      source: /my/path/to/a/file.json
```

### metronome

This sends a periodic tick downstream. It is an excellent tool to generate some test traffic to validate pipelines.

The default [codec](codecs.md#pass) is `pass`. (since we already output decoded JSON)

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-metronome://<tremor-host.local>/<config_interval>
```

Supported configuration options are:

- `interval` - The interval in which events are sent in milliseconds.

Example:

```yaml
onramp:
  - id: metronome
    type: metronome
    config:
      interval: 10000
```

### crononome

This sends a scheduled tick down the offramp. Schedules can be one-off or repeating and use a cron-like format.

Multiple cron entries can be configured, each with a symbolic name and an optional JSON payload in addition to the cron expression.

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-crononome://<tremor-host.local>
```

Supported configuration options are:

- `entries` - A sequence of entries

Example

```yaml
onramp:
  - id: crononome
    type: crononome
    codec: json
    config:
      entries:
        ## every second
        - name: 1s
          expr: "* * * * * *"
        ## every 5 seconds
        - name: 5s
          expr: "0/5 * * * * *"
        ## every minute
        - name: 1m
          expr: "0 * * * * *"
          payload:
            snot: badger
```

Cron entries that are historic or in the past ( relative to the current UTC time ) will be ignored.
Cron entries beyond 2038 will not work due to underlying libraries ( rust, chrono, cron.rs ) suffering
from the [year 2038 problem](https://en.wikipedia.org/wiki/Year_2038_problem).

### blaster

NOTE: This onramp is for benchmarking use, it should not be deployed in a live production system.

The blaster onramp is built for performance testing, but it can be used for spaced-out replays of events as well. Files to replay can be `xz` compressed. It will keep looping over the file.

The default [codec](codecs.md#json) is `json`.

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-blaster://<tremor-host.local>/<config_source_file>
```

Supported configuration options are:

- `source` - The file to read from.
- `interval` - The interval in which events are sent in nanoseconds.
- `iters` - Number of times the file will be repeated.

Example:

```yaml
onramp:
  - id: blaster
    type: blaster
    codec: json
    config:
      source: ./demo/data/data.json.xz
```

### tcp

This listens on a specified port for inbound tcp data.

The onramp can leverage preprocessors to segment data before codecs are applied and events are forwarded
to pipelines.

The default [codec](codecs.md#json) is `json`.

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-tcp://<client_ip>:<client_port>/<config_server_port>
```

Supported configuration options are:

- `host` - The IP to listen on
- `port` - The Port to listen on

Example:

```yaml
onramp:
  - id: tcp
    type: tcp
    preprocessors:
      - base64
      - lines
    codec: json
    config:
      host: "localhost"
      port: 9000
```

### rest

The rest onramp listens on a specified port for inbound RESTful ( http ) data, converting the http body as event data (and attaching other request attributes as event metadata).

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-rest://<tremor-rest-client-host.remote>
```

Supported configuration options are:

- `host` - The host to advertise as
- `port` - The TCP port to listen on

The rest onramp respects the HTTP [Content-Type header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type) and will use it to decode the request body when it's present (otherwise it defaults to using the codec specified in the onramp config).

Set metadata variables:

- `$request` - A record capturing the HTTP request attributes. Available fields within:
    - `url` - A record with the following standard URL fields (all are string-valued, except numeric port):
        - `scheme`
        - `username`
        - `password`
        - `host`
        - `port`
        - `path`
        - `query`
        - `fragment`
    - `method` - HTTP method used by the incoming request
    - `headers` - A record that maps header name (string) to values (array of strings)

Used metadata variables (for reply with linked transports):

- `$response` - A record capturing the HTTP response attributes. Available fields within:
    - `status` - Numeric HTTP status code. (optional. status code defaults to `200` when not set)
    - `headers` - A record that maps header name (string) to value (string) (optional)

When not used as a linked onramp, the status code returned with the response is `202`.

Example:

```yaml
onramp:
  - id: rest
    type: rest
    preprocessors:
      - lines
    codec: json
    config:
      host: "localhost"
      port: 9000
```

Known limitations:

It is currently not possible to configure rest onramps via swagger, RAML or OpenAPI configuration files.

### PostgreSQL

PostgreSQL onramp.

Supported configuration options are:

- `host` - PostgreSQL database hostname
- `port` - PostgresSQL database port
- `user` - Username for authentication
- `password` - Password for authentication
- `dbname` - Database name
- `query` - Query run to retrieve data
- `interval_ms` - Query interval in milliseconds
- `cache` - Location (`path`) and size (`size`) for caching of latest successful query interval

`query` must include two arguments to be filled with start and end interval timestamps.

Data will come out of onramp in objects representing columns. If schema
specifies there are two fields, `username` (`VARCHAR`) and `created_at`
(`TIMESTAMPTZ`) then the actual JSON coming out of onramp looks like:

```
"username": {
  "fieldType": "VARCHAR",
  "name": "username",
  "value": "actual\_username"
},
"created\_at": {
  "fieldType": "TIMESTAMPTZ",
  "name": "created\_at",
  "value": "2020-04-04 00:00:00.000000 +00:00"
}
```

Example:

```yml
id: db
type: postgres
codec: json
config:
  host: localhost
  port: 5432
  user: postgres
  password: example
  dbname: sales
  query: "SELECT id, name from events WHERE produced_at <= $1 AND produced_at > $2"
  interval_ms: 1000
  cache:
    path: "/path/to/cache.json"
    size: 4096
```

### ws

Websocket onramp. Receiving either binary or text packages from a websocket connection. the url is: `ws://<host>:<port>/`

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-ws://<tremor-ws-client-host.remote>
```

Supported configuration options are:

- `host` - The IP to listen on
- `port` - The Port to listen on

Set metadata variables:

- `$binary` - `true` if the incoming websocket message came as binary (`false` otherwise)

Used metadata variables (for reply with linked transports):

- `$binary` - If reply data should be send as binary instead of text (optional. data format defaults to text when not set).

Example:

```yaml
onramp:
  - id: ws
    type: ws
    codec: json
    config:
      port: 12201
      host: "127.0.0.1"
```
