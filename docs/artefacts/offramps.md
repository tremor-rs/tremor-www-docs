# Offramps

Specify how tremor connects to the outside world in order to publish to external systems.

For example, the Elastic offramp pushes data to ElasticSearch via its bulk upload REST/HTTP API endpoint.

All offramps are specified in the following form:

```yaml
offramp:
  - id: <unique offramp id>
    type: <offramp name>
    codec: <codec of the data>
    postprocessors: # can be omitted
      - <postprocessor 1>
      - <postprocessor 2>
      - ...
    preprocessors: # only for linked transport, can be omitted
      - <preprocessor 1>
      - <preprocessor 2>
      - ...
    linked: <true or false> # enable linked transport, default: false
    codec_map:
      "<mime-type>": "<codec handling the given mime-type>"
    config:
      <key>: <value>
```

## Delivery Properties

Each offramp is able to report events as being definitely sent off or as failed. It can also report itself as not functional anymore to the connected pipelines. How each offramp implements those abilities is described in the table below.

The column `Delivery acknowledgements` describes under what circumstanced the offramp considers an event delivered and acknowledges it to the connected pipelines and operators, onramps etc. therein.
Acknowledgements, Failures or missing Acknowledgements take effect e.g. when using the operators or onramps that support those mechanisms (e.g. the WAL operator or the kafka onramp).

The column `Disconnect events` describes under which circumstances this offramp is not considered functional anymore.

| Offramp   | Disconnect events | Delivery acknowledgements |
| --------- | ----------------- | ------------------------- |
| blackhole | never             | always                    |
| cb        | never             | always                    |
| debug     | never             | always                    |
| elastic   | connection loss   | on 200 replies            |
| exit      | never             | always                    |
| file      | never             | always                    |
| kafka     | see librdkafka    | see librdkafka            |
| kv        | never             | always
| newrelic  | never             | never                     |
| Postgres  | never             | always                    |
| rest      | connection loss   | on non 4xx/5xx replies    |
| stderr    | never             | always                    |
| stdout    | never             | always                    |
| tcp       | connection loss   | on send                   |
| udp       | local socket loss | on send                   |
| ws        | connection loss   | on send                   |

## System Offramps

Each tremor runtime comes with some pre-configured offramps that can be used.

### system::stdout

The offramp `/offramp/system::stdout/system` can be used to print to STDOUT. Data will be formatted as JSON.
### system::sderr

The offramp `/offramp/system::stderr/system` can be used to print to STDERR. Data will be formatted as JSON.


## Supported Offramps


### blackhole

The blackhole offramp is used for benchmarking it takes measurements of the end to end times of each event traversing the pipeline and at the end prints an HDR ( High Dynamic Range ) [histogram](http://hdrhistogram.org/).

Supported configuration options are:

- `warmup_secs` - Number of seconds after startup in which latency won't be measured to allow for a warmup delay.
- `stop_after_secs` - Stop tremor after a given number of seconds and print the histogram.
- `significant_figures` - Significant figures for the HDR histogram. (the first digits of each measurement that are kept as precise values)

Example:

```yaml
offramp:
  - id: bh
    type: blackhole
    config:
      warmup_secs: 10
      stop_after_secs: 40
```

### cb

`cb` is short for circuit breaker. This offramp can be used to trigger certain circuit breaker events manually by sending the intended circuit breaker event in the event metadata or the event data.
Supported payloads are:

 - `ack`
 - `fail`
 - `trigger` or `close`
 - `open` or `restore`

 No matter how many `ack` and `fail` strings the `cb` key contains, only ever one `ack` or `fail` CB event will be emitted, to stay within the CB protocol.
 The same is true for `trigger`/`close` and `open`/`restore` strings, only one of those two will be emitted, never more.

 Example config:

```yaml
 offramp:
   - id: cb_tester
     type: cb
```

Example payloads:

```json
{
  "cb": "ack",
  "some_other_field": true
}
```

```json
{
  "cb": ["fail", "close"]
}
```

Such an event or metadata will result in two CB insight events be sent back, one `fail` event, and one `close` event.

### debug

The debug offramp is used to get an overview of how many events are put in wich classification.

This operator does not support configuration.

Used metadata variables:

- `$class` - Class of the event to count by. (optional)

Example:

```yaml
offramp:
  - id: dbg
    type: debug
```



### elastic

The elastic offramp writes to one or more ElasticSearch nodes. This is currently tested with ES v6 and v7.

Supported configuration options are:

- `nodes` - A list of elastic search nodes to contact. These are the nodes to which tremor will send traffic to.
- `concurrency` - Maximum number of parallel requests (default: 4).

Events will be sent to the connected elasticsearch cluster via the [ES Bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) using the `index` action.
It is recommended to batch events sent to this sink using the [generic::batch operator](../tremor-query/operators.d#genericbatch) to reduce the overhead
introduced by the [ES Bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html).

The configuration options `codec` and `postprocessors` are not used, as elastic will always serialize event payloads as JSON.

If the number of parallel requests surpass `concurrency`, an error event will be emitted to the `err` port, which can be used for appropriate error handling.

The following metadata variables can be specified on a per event basis:

- `$elastic._index` - The index to write to (required).
- `$elastic._type` - The document type for elastic (optional), deprecated in ES 7.
- `$elastic._id`   - The document id for elastic (optional).
- `$elastic.pipeline` - The elastic search pipeline to use (optional).
- `$elastic.action` - The [bulk action](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) to perform, one of `delete`, `create`, `update` or `index`. If no `action` is provided it defaults to `index`. `delete` and `update` require `$elastic._id` to be set or elastic search will have error.

#### Linked Transport

If used as a linked transport, the sink will emit events in case of errors sending data to ES or if the incoming event is malformed via the `err` port.
Also, upon a returned ES Bulk request, it will emit an event for each bulk item, denoting success or failure.

Events denoting success are sent via the `out` port and have the following format:

```json
{
  "success": true,
  "source": {
    "event_id": "1:2:3",
    "origin": "file:///tmp/input.json.xz"
  },
  "payload": {}
}
```

The event metdata will contain the following:

```json
{
  "elastic": {
    "_id": "ES document id",
    "_type": "ES document type",
    "_index": "ES index",
    "version": "ES document version"
  }
}
```

Events denoting bulk item failure are sent via the `err` port and have the following format:

```json
{
  "success": false,
  "source": {
    "event_id": "2:3:4",
    "origin": null
  },
  "error": {},
  "payload": {}
}
```

`error` will contain the error description object returned from ES.

The event metadata for failed events looks as follows:

```json
{
  "elastic": {
    "_id": "ES document id",
    "_type": "ES document type",
    "_index": "ES index",
  }
}
```

For both event types `payload` is the event payload that was sent to ES.

Example Configuration:

```yaml
offramp:
  - id: es
    type: elastic
    config:
      nodes:
        - http://elastic:9200
```

Example Configuration for linked transport (including binding):

```yaml
offramp:
  - id: es-linked
    type: elastic
    linked: true
    config:
      nodes:
        - http://elastic1:9200
        - http://elastic2:9200
      concurrency: 8

binding:
  id: "es-linked-binding"
  links:
    "/onramp/example/{instance}/out": ["/pipeline/to_elastic/{instance}/in"]
    "/pipeline/to_elastic/{instance}/in": ["/offramp/es-linked/{instance}/in"]

    # handle success and error messages with different pipelines
    "/offramp/es-linked/{instance}/out": ["/pipeline/handle-es-success/{instance}/in"]
    "/offramp/es-linked/{instance}/err": ["/pipeline/handle-es-error/{instance}/in"]

    # more links...
    ...

```

### exit

The exit offramp terminates the runtime with a system exit status.

The offramp accepts events via its standard input port and responds
to events with a record structure containing a numeric exit field.

To indicate successful termination, an `exit` status of zero may be used:

```json
{ "exit": 0 }
```

To indicate non-successful termination, a non-zero `exit` status may be used:

```json
{ "exit": 1 }
```

Exit codes should follow standard UNIX/Linux guidelines when being integrated
with `bash` or other shell-based environments, as follows:

<!--alex ignore illegal-->

| Code | Meaning                                                        |
| ---- | -------------------------------------------------------------- |
| 0    | Success                                                        |
| 1    | General errors                                                 |
| 2    | Misuse of builtins                                             |
| 126  | Command invoked cannot run due to credentials/auth constraints |
| 127  | Command not understood, not well-formed or illegal             |

To delay the exit (to allow flushing of other offramps) the `delay` key can be used to delay the exit by a number of milliseconds:

```json
{
  "exit": 1,
  "delay": 1000
}
```

Example:

```yaml
offramp:
  - id: terminate
    type: exit
```

### file

The file offramp writes events to a file, one event per line. The file is overwritten if it exists.

The default [codec](codecs.md#json) is `json`.

Supported configuration options are:

- `file` - The file to write to.

Example:

```yaml
offramp:
  - id: in
    type: file
    config:
      file: /my/path/to/a/file.json
```



### kafka

The Kafka offramp connects sends events to Kafka topics. It uses librdkafka to handle connections and can use the full set of [librdkaka 1.5.0 configuration options](https://github.com/edenhill/librdkafka/blob/v1.5.0/CONFIGURATION.md).

The default [codec](codecs.md#json) is `json`.

Supported configuration options are:

- `topic` - The topic to send to.
- `brokers` - Broker servers to connect to. (Kafka nodes)
- `hostname` - Hostname to identify the client with. (default: the systems hostname)
- `key` - Key to use for messages (default: none)
- `rdkafka_options` - An optional map of option to value, where both sides need to be strings.

Used metadata variables:

- `$kafka` - Record consisting of the following meta information:
    - `$headers`: A record denoting the [headers](https://kafka.apache.org/20/javadoc/index.html?org/apache/kafka/connect/header/Header.html) for the message.
    - `$key`: Same as config `key` (optional. overrides related config param when present)

Example:

```yaml
offramp:
  - id: kafka-out
    type: kafka
    config:
      brokers:
        - kafka:9092
      topic: demo
```

### KV

The kv offramp is intended to allow for a decuple way of persisting and retrieving state in a non blocking way.

Events sent to the KV offramp are commands. The following are supported:

Example:
```yaml
  - id: kv
    type: kv
    linked: true     # this needs to be true
    codec: json
    config:
      dir: "temp/kv" # directory to store data in
```

#### get

Fetches the data for a given key.

**Request**:
```js
{"get": {"key": "<string|binary>"}}
```

**Response**:
```js
{"ok": "<decoded>"} // key was found, the format of decoded depends on the codec (does NOT have to be a string)
null,               // key was not found
```

#### put

Writes a value to a key, returns the old value if there was any.

**Request**:
```js
{"put": {
  "key": "<string|binary>",
  "value": "<to encode>" // the format of value depends on the codec (does NOT have to be a string)
}}
```

**Response**:
```js
{"ok": "<decoded>"} // key was used before, this is the old value, the format of decoded depends on the codec (does NOT have to be a string)
null,               // key was not used before
```

#### delete

Deletes a key, returns the old value if there was any.

**Request**:
```js
{"delete": {"key": "<string|binary>"}}
```

**Response**:
```js
{"ok": "<decoded>"} // key was used before, this is the old value, the format of decoded depends on the codec (does NOT have to be a string)
null,               // key was not used before
```


#### scan

Reads a range of keys

**Request**:
```js
{"scan": {
   "start": "<string|binary>", // optional, if not set will start with the first key
   "end": "<string|binary>", // optional, if not set will read to the end key
}}
```
**Response**:
```js
{"ok": [
  {
    "key": "<binary>", // keys are ALWAYS encoded as binary since we don't know if it's a string or binary
    "value": "<decoded>" // the value, the format of decoded depends on the codec (does NOT have to be a string)
  } // repeated, may be empty
]}
```

#### cas

Compare And Swap operation. Those operations require old values to match what it is compared to

**Request**:
```js
{"cas": {
   "key": "<string|binary>", // The key to operate on
   "old": "<to encode|not-set>", // The old value, if not set means "this value wasn't present"
   "new": "<to encode|not-set>", // The new value, if not set it means it gets deleted
}}
```
**Response**:

```js
{"ok": null} // The operation succeeded
{"error": {  // the operation failed
  "current": "<decoded>", // the value that is currently stored, the format of decoded depends on the codec (does NOT have to be a string)
  "proposed": "<decoded>" // the value that was proposed/expected to be there, the format of decoded depends on the codec (does NOT have to be a string)
}}
```


### newrelic

Send events to [New Relic](https://newrelic.com/) platform, using its log apis (variable by region).

This offramp encodes events as json, as this is required by the newrelic log api. Postprocessors are not used.

Supported configuration options are:

- `license_key` - New Relic's license (or insert only) key
- `compress_logs` - Whether logs should be compressed before sending to New Relic  (avoids extra egress costs but at the cost of more cpu usage by tremor) (default: false)
- `region` - Region to use to send logs. Available choices: usa, europe (default: usa)

Example:

```yaml
offramp:
  - id: newrelic
    type: newrelic
    config:
      license_key: keystring
      compress_logs: true
      region: europe
```

### PostgreSQL

PostgreSQL offramp.

Supported configuration options are:

- `host` - PostgreSQL database hostname
- `port` - PostgresSQL database port
- `user` - Username for authentication
- `password` - Password for authentication
- `dbname` - Database name
- `table` - Database table name

Data that comes in will be used to run an `INSERT` statement. It is required
that data comes in objects representing columns. The object key must represent field
name in the database and must contain following fields:

- `fieldType` - a PostgreSQL field type (e.g. `VARCHAR`, `INT4`, `TIMESTAMPTZ`,
  etc.)
- `name` - field name as represented by database table schema
- `value` - the value of the field

`codec` and `postprocessors` config values are ignored as they cannot apply to this offramp, since the event is transformed into a SQL query.

Example:

```yml
id: db
type: postgres
config:
  host: localhost
  port: 5432
  user: postgres
  password: example
  dbname: sales
  table: transactions
```

### rest

The rest offramp is used to send events to the specified endpoint.

Supported configuration options are:

- `endpoint` - Endpoint URL. Can be provided as string or as struct. The struct form is composed of the following standard URL fields:
    - `scheme` - String, required, typically `http`
    - `username` - String, optional
    - `password` - String, optional
    - `host` - String, required, hostname or ip address
    - `port` - Number, optional, defaults to `80`
    - `path` - String, optional, defaults to `/`
    - `query` - String, optional
    - `fragment` - String, optional
- `method` - HTTP method to use (default: `POST`)
- `headers` - A map of headers to set for the requests, where both sides are strings
- `concurrency` - Number of parallel in-flight requests (default: `4`)

Used metadata variables:

> Setting these metadata variables here allows users to dynamically change the behaviour of the rest offramp:

- `$endpoint` - same format as config `endpoint` (optional. overrides related config param when present)
- `$request` - A record capturing the HTTP request attributes. Available fields within:
    - `method` - same as config `method` (optional. overrides related config param when present)
    - `headers` - A map from header name (string) to header value (string or array of strings)(optional. overrides related config param when present)

These variables are aligned with the similar variables generated by the [rest onramp](./onramps.md#rest). Note that `$request.url` is not utilized here -- instead the same can be configured by setting `$endpoint` (since enabling the former here can lead to request loops when events sourced from rest onramp are fed to the rest offramp, without overriding it from the pipeline. also, `$endpoint` can be separately configured as a URL string, which is convenient for simple offramp use).

The rest offramp encodes the event as request body using the `Content-Type` header if present, using the customizable builtin `codec_map` to determine a matching coded. It falls back to use the configured codec if no `Content-Type` header is available.

When used as [Linked Transport](../operations/linked-transports.md) the same handling is applied to the incoming HTTP response, giving precedence to the `Content-Type` header and only falling back to the configured `codec`.

If the number of parallel requests surpass `concurrency`, an error event will be emitted to the `err` port, which can be used for appropriate error handling.

Set metadata variables:

> These metadata variables are used for HTTP response events emitted through the `OUT` port:

- `$response` - A record capturing the HTTP response attributes. Available fields within:
    - `status` - Numeric HTTP status code
    - `headers` - A record that maps header name (lowercase string) to value (array of strings)
- `$request` - A record with the related HTTP request attributes. Available fields within:
    - `method` - HTTP method used
    - `headers` - A record containing all the request headers
    - `endpoint` - A record containing all the fields that config `endpoint` does

When used as a linked offramp, batched events are rejected by the offramp.

Example 1:

```yaml
offramp:
  - id: rest-offramp
    type: rest
    codec: json
    postprocessors:
      - gzip
    linked: true
    config:
      endpoint:
        host: httpbin.org
        port: 80
        path: /anything
        query: "q=search"
      headers:
        "Accept": "application/json"
        "Transfer-Encoding": "gzip"
```

Example 2:

```yaml
offramp:
  - id: rest-offramp-2
    type: rest
    codec: json
    codec_map:
      "text/html": "string"
      "application/vnd.stuff": "string"
    config:
      endpoint:
        host: httpbin.org
        path: /patch
      method: PATCH
```

#### rest offramp example for InfluxDB

The structure is given for context.

```yaml
offramp:
  - id: influxdb
    type: rest
    codec: influx
    postprocessors:
      - lines
    config:
      endpoint:
        host: influx
        path: /write
        query: db=metrics
      headers:
        "Client": "Tremor"
```

### stderr

A custom stderr offramp can be configured by using this offramp type. But beware that this will share the single stderr stream with `system::stderr`.

The default codec is [json](codecs.md#json).

The stderr offramp will write a `\n` right after each event, and optionally prefix every event with a configurable `prefix`.

If the event data (after codec and postprocessing) is not a valid utf8 string (e.g. if it is binary data) if will by default output the bytes with debug formatting.
If `raw` is set to true, the event data will be put on stderr as is.

Supported configuration options:

- `prefix` - A prefix written before each event (optional string).
- `raw` - Write event data bytes as is to stderr.

Example:

```yaml
offramp:
  - id: raw_stuff
    type: stderr
    codec: json
    postprocessors:
      - snappy
    config:
      raw: true
```

### stdout

A custom stdout offramp can be configured by using this offramp type. But beware that this will share the single stdout stream with `system::stdout`.

The default codec is [json](codecs.md#json).

The stdout offramp will write a `\n` right after each event, and optionally prefix every event with a configurable `prefix`.

If the event data (after codec and postprocessing) is not a valid utf8 string (e.g. if it is binary data) if will by default output the bytes with debug formatting.
If `raw` is set to true, the event data will be put on stdout as is.

Supported configuration options:

- `prefix` - A prefix written before each event (optional string).
- `raw` - Write event data bytes as is to stdout.

Example:

```yaml
offramp:
  - id: like_a_python_repl
    type: stdout
    config:
      prefix: ">>> "
```

### tcp

This connects on a specified port for distributing outbound TCP data.

The offramp can leverage postprocessors to frame data after codecs are applied and events are forwarded
to external TCP protocol distribution endpoints.

The default [codec](codecs.md#json) is `json`.

Supported configuration options are:

- `host` - The host to advertise as
- `port` - The TCP port to listen on
- `is_non_blocking` - Is the socket configured as non-blocking ( default: false )
- `ttl` - Set the socket's time-to-live ( default: 64 )
- `is_no_delay` - Set the socket's Nagle ( delay ) algorithm to off ( default: true )

Example:

```yaml
offramp:
  - id: tcp
    type: tcp
    codec: json
    postprocessors:
      - gzip
      - base64
      - lines
    config:
      host: "localhost"
      port: 9000
```

### udp

The UDP offramp sends data to a given host and port as UDP datagram.

The default [codec](codecs.md#json) is `json`.

When the UDP onramp gets a batch of messages it will send each element of the batch as a distinct UDP datagram.

Supported configuration options are:

- `host` - the local host to send data from
- `port` - the local port to send data from
- `dst_host` - the destination host to send data to
- `dst_port` - the destination port to send data to.

Example:

```yaml
offramp:
  - id: udp-out
    type: udp
    postprocessors:
      - base64
    config:
      host: "10.11.12.13"
      port: 1234
      dst_host: "20.21.22.23"
      dst_port: 2345
```


### ws

Sends events over a WebSocket connection. Each event is a WebSocket message.

The default [codec](codecs.md#json) is `json`.

Supported configuration options are:

- `url` - WebSocket endpoint to send data to.
- `binary` - If data should be send as binary instead of text (default: `false`).

Used metadata variables:

- `$url` - same as config `url` (optional. overrides related config param when present)
- `$binary` - same as config `binary` (optional. overrides related config param when present)

Set metadata variables (for reply with [linked transports](../operations/linked-transports.md)):

- `$binary` - `true` if the websocket message reply came as binary (`false` otherwise)

When used as a linked offramp, batched events are rejected by the offramp.

Example:

```yaml
onramp:
  - id: ws
    type: ws
    config:
      url: "ws://localhost:1234"
```

# otel

CNCF OpenTelemetry offramp. Poblishes to the specified host or IP and destination TCP port via gRPC messages
conforming to the CNCF OpenTelemetry protocol specification v1. Forwards tremor value variants of `logs`, `trace`
and `metrics` messages from tremor query pipelines downstream to remote OpenTelemetry endpoints.

The offramp is experimental.

Supported configuration options are:

- `host` - String - The host or IP to listen on
- `port` - integer - The TCP port to listen on
- 'logs' - boolean - Is logging enabled for this instance. Defaults to `true`. Received `logs` events are dropped when `false`.
- 'metrics' - boolean - Is metrics enabled for this instance. Defaults  to `true`. Defaults to `true`. Received `metrics` events are dropped when `false`.
- 'trace' - boolean - Is trace enabled for this instance. Defaults to `true`. Defaults to `true`. Received `trace` events are dopped when `false`.

Pipelines that leverage the OpenTelemetry integration can use utility modules in the `cncf::otel` module to
simplify working with the tremor value mapping of the event data. The connector translates the tremor value level
data to protocol buffers automatically for distribution to downstream OpenTelemetry systems.

The connector can be used with the `qos::wal` operator for transient in-memory or persistent disk-based guaranteed delivery. If either
tremor or the downstream system fails or becomes uncontactable users can configure ( bytes and/or number of messages retained ) retention
for lossless recovery. For events marked as transitional that are explicitly acknowledged, `fail` insights are propagated for events that
are not succesfully transmitted downstream. Non-transactional events ( those not marked as transactional ) are delivered on a best effort
basis. Regardless of the transaction configuration, when paired with qos operators upstream pipelines, the sink will coordinate failover
and recovery to the configured retention, replaying the retained messages upon recovery of network accessibility of the downstream endpoints.

For best effort delivery - the `qos::wal` can be omitted and events distributed when downstream endpoints are inaccessible will be
lost.

Example:

```yaml
onramp:
  - id: otlp
    type: otel
    codec: json
    config:
      port: 4317
      host: 10.0.2.1
```
