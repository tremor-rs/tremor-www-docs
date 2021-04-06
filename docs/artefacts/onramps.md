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
    postprocessors: # only for linked transport, can be omitted
      - <postprocessor 1>
      - <postprocessor 2>
      - ...
    linked: <true or false> # enable linked transport, default: false
    codec: <codec of the data>
    codec_map:
      "<mime-type>": <coded handling events of this mime-type>
    config:
      <key>: <value>
```

The [`codec`](codecs.md) field is optional and if not provided will use onramps default codec.

The `err_required` field can be set to `true` if the onramp should not start unless both `out` and `err` ports are connected to at least one pipeline.

The `config` contains a map (key-value pairs) specific to the onramp type.

## Delivery Properties

Onramps are able to act upon both circuit breaker and guaranteed delivery events from the downstream pipelines. Those are triggered when event delivery is acknowledged or when event delivery fails. Also when some part (offramps, operators) signals itself being broken, the circuit breaker opens, or when the downstream system heals, the circuit breaker closes again, signalling it is safe to send further events. How each onramp reacts, is described in the table below:

The column `Delivery Acknowledgements` describes when the onramp considers and reports the event delivered to the upstream it is connected to.

Onramp     | Delivery Acknowledgements                                           |
-----------|---------------------------------------------------------------------|
blaster    | not supported                                                       |
cb         | not supported                                                       |
crononome  | not supported                                                       |
discord    | not supported                                                       |
file       | not supported                                                       |
kafka      | always, only on `ack` event if `enable.auto.commit` is set to false |
metronome  | not supported                                                       |
nats       | not supported                                                       |
PostgreSQL | not supported                                                       |
rest       | not supported                                                       |
stdin      | not supported                                                       |
tcp        | not supported                                                       |
udp        | not supported                                                       |
ws         | not supported                                                       |


## Supported Onramps
### blaster

!!!note

    This onramp is for benchmarking use, it should not be deployed in a live production system.

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
### cb

The `cb` onramp is for testing how downstream pipeline and offramps issue circuit breaker events. It expects a circuit breaker event for each event it sent out, and then, the latest after the configured `timeout` is exceeded, it exits the tremor process. If some events didn't receive circuit breaker events, it exits with status code `1`, if everything is fine it exits with `0`.

Supported configuration options are:

- `source` - The file to read from, expecting 1 event payload per line.
- `timeout` - The time to wait for circuit breaker events in milliseconds. If this timeout is exceeded, the tremor process is terminated. (Default: 10000 ms)

Example:

```yaml
onramp:
  - id: cb_test
    type: cb
    codec: json
    config:
      source: in.json
      timeout: 1000
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

### discord

**This onramp can be linked**

The `discord` onramp allows consuming events from the [Discord API](https://discord.com/developers/docs/intro). It uses the event structure as provided by [serenity](https://docs.rs/serenity/0.10.2/serenity/) wrapped in event-named records.

Replies send to this onramp can perform multiple operations:

#### Guild related
```json
{"guild": {
  "id": 1234,         // guild id, required
  // member section required
  "member": {
    "id": 2345,      // member id, required

    // Roles to remove, optional
    "remove_roles": [
      3456, // ... role ids
    ],
    // Roles to add, optional
    "add_roles": [
      4567, // ... role ids
    ],
    "deafen": true, // (un)deafen the member, optional
    "mute": true, // (un)deafen the member, optional
  },

}}
```
#### Message related
```json
{"message": {
  "channel_id": 1234, // channel id, required
  // Update message section, optional
  "update": {
    "message_id": 2345, // message id to update, required
    // Reactions to add
    "add_reactions": [
      "😀", // emoji reaction
      {  // custom reaction
        "id": 3456, // emoji id, required
        "name": "seal-of-approval" // emoji name, optional
        "animated": true, // animated, optional
       }
       // ...
    ],
  },
  // Send section, optional
  "send": {
    "content": "hello!", // message content, optional,
    "reference_message": 4567, // Reference to other message, optional
    "reference_channel": 5678, // reference channel, optional, default is `channel_id` (ignored w/o `reference_message`)
    "tts": false, // use text to speech, optional
    // Embed section, optional
    "embed": {

      // Author section, optional
      "author": {
        "icon_url": "https://...", // url of the author icon, optional
        "name": "Snottus Badgerus", // name of the author, optional
        "url": "https://...", // url of the author profile, optional
      },
      "colour": 0, // color (as number) of the embed, optional (hint: use hex in tremor script it makes it easier)\
      "description": "This is an embed", // A description for the embed, optional
      // Embedded fields, optional
      "fields": [
        {
          "name": "field 1", // name of the field, required
          "value": "explenation", // 'body' of the field, required
          "inline": true, // if the field should be inlined, optional, default: false
        }
        // ...
      ],
      "footer": "look at my feet!", // simple footer, optional
      // Footer section, optional, alternative to simple footer
      "footer": {
        "text": "look at my feet!", // footer text, optional
        "icon_url": "https://...", // footer icon, optional
      }
    },
    // Reactions to add
    "reactions": [
      "😀", // emoji reaction
      {  // custom reaction
        "id": 3456, // emoji id, required
        "name": "seal-of-approval" // emoji name, optional
        "animated": true, // animated, optional
       }
       // ...
    ],
  }
}}
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
- `sleep_on_done` - Waits for the given number of milliseconds, before terminating tremor. Intended to be used with `close_on_done`.

Example:

```yaml
onramp:
  - id: in
    type: file
    config:
      source: /my/path/to/a/file.json
      close_on_done: true
      sleep_on_done: 1000 # wait for a second before terminating
```



### kafka

The Kafka onramp connects to one or more Kafka topics. It uses librdkafka to handle connections and can use the full set of [librdkafka 1.5.0 configuration options](https://github.com/edenhill/librdkafka/blob/v1.5.0/CONFIGURATION.md).

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
- `retry_failed_events` - If set to `false` the source will **not** seek back the consumer offset upon a failed events and thus not retry those when `enable.auto.commit` is set to `false` in `rdkafka_options`. (default `true`)
- `poll_interval` - Duration in milliseconds to wait until we poll again if no message is in the kafka queue. (default: `100`)

Set metadata variables are:

- `$kafka` - Record consisting of two optional keys:
    - `headers`: A record denoting the [headers](https://kafka.apache.org/20/javadoc/index.html?org/apache/kafka/connect/header/Header.html) for the message (if any).
    - `key`: The key used for this message in bytes (if any).
    - `topic`: The topic the message was on (if any).
    - `offset`: The offset in the partition the message was on (if any).
    - `partition`: The partition the message was on (if any).
    - `timestamp`: The timestamp provided by kafka in milliseconds (if any).
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

A more involved example, only committing on successful circuit breaker event and not retrying failed events, while also decreasing the poll interval to 10ms to get notified of new messages faster:

```yaml
onramp:
  - id: involved-kafka
    type: kafka
    codec: msgpack
    preprocessors:
      - lines
    config:
      brokers:
        - kafka01:9092
        - kafka02:9092
      topics:
        - my_topic
      group_id: my_group_id
      retry_failed_events: false
      poll_interval: 10
      rdkafka_options:
        'enable.auto.commit': false
```

#### Semantics with `enable.auto.commit`

If `enable.auto.commit: false` is set in `rdkafka_options`, the consumer offset in kafka will only be committed when the event has been successfully reached the other end of the pipeline (typically some [offramp](offramps.md#offramps) ).
If an event failed during processing within the pipeline or at a downstream offramp, the consumer offset will be reset to the offset of the failed event, so it will be retried. This has some consequences worth mentioning:

* Already processed kafka messages (that have succeeded before the failed message failed) might be seen again multiple times.
* If the message is persistently failing (e.g. due to an illegal payload or similar), tremor will retry those messages infinitely.

If persistent failures are to be expected (e.g. due to invalid event payloads) or if repeating messages in general are a problem for the application, avoiding retries with `retry_failed_events: false` is advised.

If `enable.auto.commit: true` is set in `rdkafka_options`, which is the default behaviour if nothing is specified, the offset is immediately committed upon event reception in tremor, regardless of success or failure of processing the kafka message as event in tremor.

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

### nats
The nats onramp connects to nats server(s) and subscribes to a specified subject.

The default [codec](codecs.md#json) is `json`. 

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-nats://<config_first_host_host_addr>[:<config_first_host_port>]/<subject>
```

Supported configuration operations are:

- `hosts` - List of hosts to connect to.
- `subject` - Subject to subscribe to for listening to messages.
- `queue` - Optional queue to subscribe to.
- `options` - Optional struct, which can be used to customise the connection to the server (see [`nats.rs` configuration options](https://docs.rs/nats/0.9.8/nats/struct.Options.html) for more info):
    - `token`: String; authenticate using a token.
    - `username`: String; authenticate using a username and password.
    - `password`: String; authenticate using a username and password.
    - `credentials_path`: String; path to a `.creds` file for authentication.
    -  `cert_path`: String; path to the client certificate file.
    -  `key_path`: String; path to private key file.
    -  `name`: String; name this configuration.
    -  `echo`: Boolean; if true, published messages will not be delivered.
    -  `max_reconnects`: Integer; max number of reconnection attempts.
    -  `reconnect_buffer_size`: Integer; max amount of bytes to buffer when accepting outgoing traffic in disconnected mode.
    -  `tls`: Boolean; if true, sets tls for _all_ server connections.
    -  `root_cert`: String; path to a root certificate.

Set metadata variables are:

- `$nats`: Record consisting of the following metadata:

    - `$reply`: Reply associated with the message (if any).
    - `$headers`: Record denoting the headers for the message (if any).

Example:
```yaml
onramp:
  - id: nats-in
    type: nats
    config:
      hosts:
        - "127.0.0.1:4444"
      subject: demo
      queue: stack
      options:
        name: nats-demo
        reconnect_buffer_size: 1
```

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

### rest

**This onramp can be linked**

The rest onramp listens on a specified port for inbound RESTful ( http ) data, treating the decoded and preprocessed http body as event data (and attaching other request attributes as event metadata).

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-rest://<tremor-rest-client-host.remote>
```

Supported configuration options are:

- `host` - The host to advertise as
- `port` - The TCP port to listen on

The rest onramp respects the HTTP [Content-Type header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type) and will use it to decode the request body when it's present (otherwise it defaults to using the codec specified in the onramp config).

Tremor supports a limited set of builtin codecs used for well known MIME types (e.g. `application/json`, `application/yaml`, `text/plain`). In order to customize how certain `Content-Type`s are handled, provide a `codec_map` providing a mapping from MIME type to Tremor codec in the top level artifact config (where the `codec` is set).

Set metadata variables:

- `$request` - A record capturing the HTTP request attributes. Available fields within:
    - `url` - A record with the following standard URL fields (optional fields might not be present):
        - `scheme` - String, typically `http`
        - `username` - String, optional
        - `password` - String, optional
        - `host` - String
        - `port` - number, optional, absence means `80`
        - `path` - String
        - `query` - String, optional
        - `fragment` - String, optional
    - `method` - HTTP method used by the incoming request
    - `headers` - A record that maps header name (lowercase string) to values (array of strings)

Used metadata variables:

> These variables can be used to dynamically change how responses are handled when using this onramp as [linked transport](../operations/linked-transports.md):

- `$response` - A record capturing the HTTP response attributes. Available fields within:
    - `status` - Numeric HTTP status code. (optional. status code defaults to `200` when not set)
    - `headers` - A record that maps header name (string) to value (string or array of strings) (optional)

When not used as a linked onramp, the status code returned with the response is `202`.

Example:

```yaml
onramp:
  - id: rest
    type: rest
    preprocessors:
      - lines
    codec: json
    codec_map:
      "text/html": "string"
    config:
      host: "localhost"
      port: 9000
```

Known limitations:

It is currently not possible to configure rest onramps via swagger, RAML or OpenAPI configuration files.

### stdin

An oramp which takes input from `stdin`.

The default [codec](codecs.md#string) is `string`.

The event [origin URI](../tremor-script/stdlib/tremor/origin.md) set by the onramp is of the form:

```
tremor-stdin://<tremor-host.local>
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
      host: "127.0.0.1"
      port: 9000
```

#### tcp onramp example for [GELF](https://docs.graylog.org/en/latest/pages/gelf.html#gelf-via-tcp)

```yaml
onramp:
  - id: gelf-tcp
    type: tcp
    preprocessors:
      - lines-null
    codec: json
    config:
      host: "127.0.0.1"
      port: 12201
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
    codec: json
    config:
      host: "127.0.0.1"
      port: 9000
```

#### udp onramp example for [GELF](https://docs.graylog.org/en/latest/pages/gelf.html#gelf-via-udp)

```yaml
onramp:
  - id: gelf-udp
    type: udp
    preprocessors:
      - decompress
      - gelf-chunking
      - decompress
    codec: json
    config:
      host: "127.0.0.1"
      port: 12201
```

### ws

**This onramp can be linked**

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

Used metadata variables (for reply with [linked transports](../operations/linked-transports.md)):

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
# otel

CNCF OpenTelemetry onramp. Listens on TCP port `4317` for gRPC traffic conforming to the CNCF OpenTelemetry protocol specification.
Forwards tremor value variants of `logs`, `trace` and `metrics` messages.

The onramp is experimental.

Supported configuration options are:

- `host` - String - The host or IP to listen on
- `port` - integer - The TCP port to listen on
- 'logs' - boolean - Is logging enabled for this instance. Defaults to `true`. Received `logs` events are dropped when `false`.
- 'metrics' - boolean - Is metrics enabled for this instance. Defaults  to `true`. Defaults to `true`. Received `metrics` events are dropped when `false`.
- 'trace' - boolean - Is trace enabled for this instance. Defaults to `true`. Defaults to `true`. Received `trace` events are dopped when `false`.

Pipelines that leverage the OpenTelemetry integration can use utility modules in the `cncf::otel` module to
simplify working with the tremor value mapping of the event data. The connector translates the wire level
data from protocol buffers to tremor values automatically.

Example:

```yaml
onramp:
  - id: otlp
    type: otel
    codec: json
    config:
      port: 4317
      host: 127.0.0.1
```