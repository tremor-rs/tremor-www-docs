# Offramps

Specify how tremor connects to the outside world in order to publish to external systems.

For example, the Elastic offramp pushes data to ElasticSearch via its bulk upload REST/HTTP API endpoint.

All `offramps` are specified in the following form:

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

The column `Delivery acknowledgements` describes under what circumstances the offramp considers an event delivered and acknowledges it to the connected pipelines and operators, onramps etc. therein.
Acknowledgements, Failures or missing Acknowledgements take effect e.g. when using the operators or onramps that support those mechanisms (e.g. the WAL operator or the Kafka onramp).

The column `Disconnect events` describes under which circumstances this offramp is not considered functional anymore.

| Offramp   | Disconnect events | Delivery acknowledgements |
| --------- | ----------------- | ------------------------- |
| amqp      | never             | always                    |
| blackhole | never             | always                    |
| cb        | never             | always                    |
| debug     | never             | always                    |
| dns       | never             | always                    |
| elastic   | connection loss   | on 200 replies            |
| exit      | never             | always                    |
| file      | never             | always                    |
| gcs       | connection loss   | on successful send        |
| gpub      | connection loss   | on successful send        |
| kafka     | see librdkafka    | see librdkafka            |
| kv        | never             | always                    |
| nats      | connection loss   | always                    |
| newrelic  | never             | never                     |
| otel      | connection loss   | on successful delivery    |
| Postgres  | never             | always                    |
| rest      | connection loss   | on non 4xx/5xx replies    |
| stderr    | never             | always                    |
| stdout    | never             | always                    |
| tcp       | connection loss   | on send                   |
| udp       | local socket loss | on send                   |
| ws        | connection loss   | on send                   |

## System Offramps

Each tremor runtime comes with some pre-configured `offramps` that can be used.

### system::stdout

The offramp `/offramp/system::stdout/system` can be used to print to STDOUT. Data will be formatted as JSON.
### system::stderr

The offramp `/offramp/system::stderr/system` can be used to print to STDERR. Data will be formatted as JSON.


## Supported Offramps


### amqp

The amqp offramp publishes AMQP messages to an [AMQP](https://www.amqp.org) broker. It uses [lapin](https://docs.rs/lapin/1.6.8/lapin/) for an AMQP 0.9.1 protocol implementation.

Example:

```yaml
offramp:
  - id: amqp
    type: amqp
    config:
      amqp_addr: "amqp://guest:guest@127.0.0.1:5672/"
      exchange: ""
      routing_key: "hello"
      publish_options:
        immediate: true
        mandatory: false
```
Supported configuration options are:

- `amqp_addr` - an AMQP URI as string, required. For more details see [AMQP 0.9.1 URI spec](https://www.rabbitmq.com/uri-spec.html).
- `exchange` - The exchange to publish messages to. Format: String, optional, defaults to the empty string and then publish to the default exchange.
- `routing_key` - Specifies the routing key for the message. The routing key is used for routing messages depending on the exchange configuration. Format: String, optional, defaults to the empty string.
- `publish_options` - Required config that controls what happens when a message cannot be routed to a queue
  - `immediate` - This flag tells the server how to react if the message cannot be routed to a queue consumer immediately. If this flag is `true`, the server will return an undeliverable message with a Return method. If this flag is `false`, the server will queue the message, but with no guarantee that it will ever be consumed. Default: `false`.
  - `mandatory` - This flag tells the server how to react if the message cannot be routed to a queue. If this flag is `true`, the server will return an unroutable message with a Return method. If this flag is false, the server silently drops the message. Default: `false`.

Events are published (after being serialized and possibly chunked codec and postprocessors) as AMQP Messages to the specified `exchange` (empty string is the default exchange) using the specified routing key.

This offramp uses the AMQP 0.9.1 [basic-publish operation](https://www.rabbitmq.com/amqp-0-9-1-reference.html#basic.publish).

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

The debug offramp is used to get an overview of how many events are put in which classification.

This operator does not support configuration.

Used metadata variables:

- `$class` - Class of the event to count by. (optional)

Example:

```yaml
offramp:
  - id: dbg
    type: debug
```


### dns

The `dns` linked offramp allows performing DNS queries against the system resolver.

!!! note

    No codecs, configuration, or processors are supported.

Example:
```yaml
  - id: dns
    type: dns
```

The event needs the following structure:

```json
{
  "lookup": "tremor.rs"
}
```

```json
{
  "lookup": {
    "name": "tremor.rs",
    "type": "CNAME"
  }
}
```

where type can be one of (please consult your DNS manual for the meaning of each):

* `A`
* `AAAA`
* `ANAME`
* `CNAME`
* `TXT`
* `PTR`
* `CAA`
* `HINFO`
* `HTTPS`
* `MX`
* `NAPTR`
* `NULL`
* `NS`
* `OPENPGPKEY`
* `SOA`
* `SRV`
* `SSHFP`
* `SVCB`
* `TLSA`

!!! note

    If type is not specified `A` records will be looked up


Responses are an Array of objects denoting the type of record found as a key, followed by the entry as a string and a `ttl` for the record (please consult your DNS manual for the return value of different record types):

```json
[
  {"A": "1.2.3.4", "ttl": 60},
  {"CNAME": "www.tremor.rs", "ttl": 120}
]
```

### elastic

The elastic offramp writes to one or more ElasticSearch nodes. This is currently tested with ES v6 and v7.

Supported configuration options are:

- `nodes` - A list of elastic search nodes to contact. These are the nodes to which tremor will send traffic to.
- `concurrency` - Maximum number of parallel requests (default: 4).

Events will be sent to the connected ElasticSearch cluster via the [ES Bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) using the `index` action.
It is recommended to batch events sent to this sink using the [generic::batch operator](../tremor-query/operators.md#genericbatch) to reduce the overhead
introduced by the [ES Bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html).

The configuration options `codec` and `postprocessors` are not used, as elastic will always serialize event payloads as JSON.

If the number of parallel requests surpass `concurrency`, an error event will be emitted to the `err` port, which can be used for appropriate error handling.

The following metadata variables can be specified on a per event basis:

- `$elastic["_index"]` - The index to write to (required).
- `$elastic["_type"]` - The document type for elastic (optional), deprecated in ES 7.
- `$elastic["_id"]`   - The document id for elastic (optional).
- `$elastic.pipeline` - The ElasticSearch pipeline to use (optional).
- `$elastic.action` - The [bulk action](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) to perform, one of `delete`, `create`, `update` or `index`. If no `action` is provided it defaults to `index`. `delete` and `update` require `$elastic._id` to be set or elastic search will have error.

#### Linked Transport

If used as a linked transport, the sink will emit events in case of errors sending data to ES or if the incoming event is malformed via the `err` port.
Also, upon a returned ES Bulk request, it will emit an event for each bulk item, denoting success or failure.

*Success Responses*

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

The event metadata will contain the following:

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

*Error Responses*

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

Error Responses that are not scoped to bulk items, but the whole operation of turning the event into a Elasticsearch Bulk Request and sending that request to Elasticsearch
will have the same payload format as Bulk item errors, but the `$elastic` metadata is missing:

```json
{
  "success": false,
  "source": {
    "event_id": "2:3:4",
    "origin": "tremor-rest://example.org/"
  },
  "error": {},
  "payload": {}
}
```

For both error and success responses `payload` is the event payload that was sent to ES.

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

To delay the exit (to allow flushing of other `offramps`) the `delay` key can be used to delay the exit by a number of milliseconds:

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

### gcs

Google Cloud Storage offramp.

This offramp can issue basic operations to list buckets and objects and to create, insert and delete objects from the Google Cloud Platform cloud storage service.

!!! note

    The offramp is experimental.

This offramp assumes that the environment variable `GOOGLE_APPLICATION_CREDENTIALS` been exported to the execution environment and it has been configured to point to a valid non-expired service account token json file.


Example:

```yaml
offramp:
  - id: gcs
    type: gcs
    codec: json
    linked: true
    postprocessors:
      - gzip   
    preprocessors:
      - gzip 
```

If the use case for the offramp requires metadata from the Google Cloud Storage service on the supported operations for this offramp, then set linked to true and configure the output port `out`.
If the use case does not require metadata, then set linked to false.


#### list_buckets

Lists all the buckets in the Google Cloud Storage project.

**Request**:
```js
{
 "command": "list_buckets",
 "project_id": "<project-id>"
}
```

**Response**:
```js
[
  {
    "cmd": "list_buckets",
    "data": {
      "items": [
        {
          "location": "EU",
          "id": "<bucket-id>",
          "locationType": "multi-region",
          "storageClass": "STANDARD",
          "metageneration": "4",
          "selfLink": "https://www.googleapis.com/storage/v1/b/<bucket-id>",
          "kind": "storage#bucket",
          "name": "<bucket-name>",
          "timeCreated": "<time of creation>",
          "iamConfiguration": {
            "uniformBucketLevelAccess": {
              "enabled": true,
              "lockedTime": "2021-06-17T09:12:22.122Z"
            },
            "bucketPolicyOnly": {
              "enabled": true,
              "lockedTime": "2021-06-17T09:12:22.122Z"
            }
          },
          "etag": "CAQ=",
          "defaultEventBasedHold": false,
          "retentionPolicy": {
            "effectiveTime": "2021-03-19T09:12:22.122Z",
            "retentionPeriod": "60",
            "isLocked": false
          },
          "updated": "2021-04-13T17:05:29.404Z",
          "satisfiesPZS": false,
          "projectNumber": "<project-number>"
        }
      ],
      "kind": "storage#buckets"
    }
  }
]

```

***Where***

- `<project-id>` - The project id of the Google Cloud Storage project where the buckets are.
- `<bucket-id>` - The unique identifier of the bucket.
- `<project-number>` - The project number for the Google Cloud Storage project.


#### list_objects

Lists all the objects in the specified bucket.

**Request**:
```js
{
  "command": "list_objects",
  "bucket": "<bucket-name>"
}
```

**Response**:
```js
[
  {
    "cmd": "list_objects",
    "data": {
      "items": [
        {
          "mediaLink": "",
          "bucket": "<bucket-name>",
          "id": "<object-id>",
          "size": "1943550",
          "crc32c": "0QXXmA==",
          "storageClass": "STANDARD",
          "generation": "1616145246990906",
          "metageneration": "1",
          "timeStorageClassUpdated": "2021-03-19T09:14:07.012Z",
          "selfLink": "",
          "kind": "storage#object",
          "name": "<object-name>",
          "md5Hash": "ucrP5b1N+6JHxn1TKavn/A==",
          "timeCreated": "2021-03-19T09:14:07.012Z",
          "etag": "CLrk6JqCvO8CEAE=",
          "updated": "2021-03-19T09:14:07.012Z",
          "retentionExpirationTime": "2021-03-19T09:15:07.012Z",
          "contentType": "<content-type>"
        }
      ],
      "kind": "storage#objects"
    }
  }
]

```

***Where***

- `<bucket-name>` - The name of the Google Cloud Storage bucket where the object is.
- `<object-id>` - The unique object identifier.
- `<object-name>` - The name of the object in the Google Cloud Stoarge bucket.
- `<content-type>` - The type of the object uploaded.


#### create_bucket

Creates a bucket in the project specified in the command.

**Request**:
```js
{
  "command": "create_bucket" ,
  "project_id": "<project-id>",
  "bucket": "<bucket>"
}
```

**Response**:
```js
[
  {
    "cmd": "create_bucket",
    "data": {
      "projectNumber": "<project-number>",
      "location": "US",
      "id": "<bucket-id>",
      "etag": "CAE=",
      "locationType": "multi-region",
      "storageClass": "STANDARD",
      "metageneration": "1",
      "updated": "2021-04-22T07:37:23.702Z",
      "selfLink": "https://www.googleapis.com/storage/v1/b/<bucket-name>",
      "kind": "storage#bucket",
      "name": "tremor",
      "iamConfiguration": {
        "uniformBucketLevelAccess": {
          "enabled": false
        },
        "bucketPolicyOnly": {
          "enabled": false
        }
      },
      "timeCreated": "2021-04-22T07:37:23.702Z"
    }
  }
]
```

***Where***

- `<project-id>` - The project id of the Google Cloud Storage project where the bucket is.
- `<bucket-id>` - The unique identifier of the bucket.
- `<project-number>` - The project number for the Google Cloud Storage project.


#### remove_bucket

Removes the bucket from the specified project in Google Cloud Storage project.

**Request**:
```js
{
 "command": "remove_bucket",
 "bucket": "<bucket-name>"
}
```
**Response**:
```js
```

***Where***

- `<bucket-name>` - The name of the Google Cloud Storage bucket where the object is.


#### upload_object

Uploads the object to a Google Cloud Storage bucket.

**Request**:
```js
{
 "command": "upload_object",
 "bucket": "<bucket-name>",
 "object": "<object-name>",
 "body": `<object>`
}
```

**Response**:
```js
[
  {
    "cmd": "upload_object",
    "data": {
      "mediaLink": "https://storage.googleapis.com/download/storage/v1/b/<bucket-name>/o/<object-name>?generation=1619077199260663&alt=media",
      "bucket": "<bucket-name>",
      "id": "<object-id>",
      "size": "47",
      "crc32c": "a7mrxw==",
      "storageClass": "STANDARD",
      "generation": "1619077199260663",
      "metageneration": "1",
      "timeStorageClassUpdated": "2021-04-22T07:39:59.278Z",
      "selfLink": "https://www.googleapis.com/storage/v1/b/<bucket-name>/o/<object-name>",
      "kind": "storage#object",
      "name": "april",
      "md5Hash": "qhr9326j+3PeIK9koXMHCg==",
      "timeCreated": "2021-04-22T07:39:59.278Z",
      "etag": "CPfXzcqskfACEAE=",
      "updated": "2021-04-22T07:39:59.278Z",
      "retentionExpirationTime": "2021-04-22T07:40:59.278Z",
      "contentType": "application/json"
    }
  }
]
```

***Where***

- `<object>` - The object data to be uploaded to a Google Cloud Storage bucket.
- `<bucket-name>` - The name of the Google Cloud Storage bucket where the object is.
- `<object-id>` - The unique object identifier.
- `<object-name>` - The name of the object in the Google Cloud Stoarge bucket.


#### fetch_object

Returns the metadata for the object fetched.

**Request**:
```js
{
 "command": "fetch",
 "bucket": "<bucket-name>",
 "object": "<object-name>"
}

```

**Response**:
```js
[
  {
    "cmd": "fetch",
    "data": {
      "mediaLink": "https://storage.googleapis.com/download/storage/v1/b/<bucket-name>/o/<object-name>?generation=1619077199260663&alt=media",
      "bucket": "<bucket-name>",
      "id": "<object-id>",
      "size": "47",
      "crc32c": "a7mrxw==",
      "storageClass": "STANDARD",
      "generation": "1619077199260663",
      "metageneration": "1",
      "timeStorageClassUpdated": "2021-04-22T07:39:59.278Z",
      "selfLink": "https://www.googleapis.com/storage/v1/b/<bucket-name>/o/<object-name>",
      "kind": "storage#object",
      "name": "april",
      "md5Hash": "qhr9326j+3PeIK9koXMHCg==",
      "timeCreated": "2021-04-22T07:39:59.278Z",
      "etag": "CPfXzcqskfACEAE=",
      "updated": "2021-04-22T07:39:59.278Z",
      "retentionExpirationTime": "2021-04-22T07:40:59.278Z",
      "contentType": "application/json"
    }
  }
]
```

***Where***

- `<bucket-name>` - The name of the Google Cloud Storage bucket where the object is.
- `<object-id>` - The unique object identifier.
- `<object-name>` - The name of the object in the Google Cloud Stoarge bucket.


#### download_object

Downloads the object.

**Request**:
```js
{
  "command": "download_object",
  "bucket": "<bucket-name>",
  "object": "<object-name>"
}
```

**Response**:
```js
[
  {
    "cmd": "download_object",
    "data": `<object>`
  }
]
```

***Where***

- `<bucket-name>` - The name of the Google Cloud Storage bucket where the object is.
- `<object-name>` - The name of the object in the Google Cloud Stoarge bucket.
- `<object>` - The object downloaded.


#### remove_object

Removes the object from the specified bucket.

**Request**:
```js
{
  "command": "remove_object" ,
  "bucket":"<bucket-name>",
  "object": "<object-name>"
}
```

**Response**:
```js

```

***Where***

- `<bucket-name>` - The name of the Google Cloud Storage bucket where the object is.
- `<object-name>` - The name of the object in the Google Cloud Stoarge bucket.



### gpub

Google Cloud Pubsub - Publisher

This offramp can issue basic operation of creating a subscription and sending a message to a topic.

!!! note

    The offramp is experimental.

This offramp assumes that the environment variable `GOOGLE_APPLICATION_CREDENTIALS` has been exported to the execution environment and it has been configured to point to a valid non-expired service account token json file.

Supported configuration options are:

- `pem` - The pem file from GCP for authentication.


Example:

```yaml
offramp:
  - id: gpub
    type: gpub
    codec: json
    postprocessors:
      - gzip    
    linked: true
    config:
      pem: gcp.pem
```
If the use case for the offramp requires metadata from the Google Cloud Pub/Sub service on the supported operations for this offramp, then set linked to true and configure the output port `out`. If the use case does not require metadata, then set linked to false.

#### create_subscription

Create a subsrciption to a pub/sub topic.

**Request**:
```js
{
  "command": "create_subscription",
  "project": "<project-id>",
  "topic": "<topic-name>",
  "subscription": "<subscription-name>",
  "message_ordering": `<message-ordering>`
}
```

**Response**:
```js
{
  "subscription": "projects/<project-id>/subscriptions/<subscription-name>",
  "topic": "projects/<project-id>/topics/<topic-name>",
  "ack_deadline_seconds": `<ack_deadline_seconds>`,
  "retain_acked_messages": `<retain_acked_messages>`,
  "enable_message_ordering": `<enable_message_ordering>`,
  "message_retention_duration": `<message_retention_duration>`,
  "filter": "<filter>",
  "detached": `<detached>`
}
```

***Where***

- `<project-id>` - The project id of the Google Cloud Pub/sub project where the topic is.
- `<topic-name>` - The Google cloud Pub/Sub topic name to which the subscription is being created.
- `<subscription-name>` - Set a unique name for the subscription to be created.
- `<message-ordering>` - Can be set to true or false. To receive the messages in order, set the message ordering property on the subscription you receive messages from. Receiving messages in order might increase latency.
- `<ack_deadline_seconds>` - The approximate amount of time (on a best-effort basis) Pub/Sub waits for the subscriber to acknowledge receipt before resending the message. In the interval after the message is delivered and before it is acknowledged, it is considered to be outstanding. During that time period, the message will not be redelivered (on a best-effort basis).
- `<retain_acked_messages>` -  Indicates whether to retain acknowledged messages. If true, then messages are not expunged from the subscription's backlog, even if they are acknowledged, until they fall out of the message_retention_duration window.
- `<enable_message_ordering>` - If true, messages published with the same ordering_key in PubsubMessage will be delivered to the subscribers in the order in which they are received by the Pub/Sub system. Otherwise, they may be delivered in any order.
- `<message_retention_duration>` - How long to retain unacknowledged messages in the subscription's backlog, from the moment a message is published. If retain_acked_messages is true, then this also configures the retention of acknowledged messages, and thus configures how far back in time a Seek can be done. Defaults to 7 days. Cannot be more than 7 days or less than 10 minutes.
- `<filter>` - An expression written in the Pub/Sub filter language. If non-empty, then only PubsubMessages whose attributes field matches the filter are delivered on this subscription. If empty, then no messages are filtered out.
- `<detached>` - Indicates whether the subscription is detached from its topic. Detached subscriptions don't receive messages from their topic and don't retain any backlog.


#### send_message

Send a message to a pubsub topic.

**Request**:
```js
{
  "command": "send_message", 
  "project": "<project-id>", 
  "topic": "<topic-name>", 
  "data": `<data>`,
  "ordering_key": "<ordering-key>" 
}
```

**Response**:
```js
{
  "message-id": "<message-id>",
  "command": "send_message"
}
```

***Where***

- `<project-id>` - The project id of the Google Cloud Pubsub project where the topic is.
- `<topic-name>` - The Google cloud PubSub topic name to which the message is being sent.
- `<data>` - The data that is to be sent as message.
- `<ordering-key>` - If non-empty, identifies related messages for which publish order should be respected. If a Subscription has message_ordering set to true, messages published with the same non-empty ordering_key value will be delivered to subscribers in the order in which they are received by the pub/sub system. All PubsubMessages published in a given PublishRequest must specify the same ordering_key value. 
- `<message-id>` - The message id assigned by the Google Cloud pub/sub api.



### Kafka

The Kafka offramp connects sends events to Kafka topics. It uses `librdkafka` to handle connections and can use the full set of [librdkaka 1.5.0 configuration options](https://github.com/edenhill/librdkafka/blob/v1.5.0/CONFIGURATION.md).

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

### kv

The `kv` offramp is intended to allow for a decoupled way of persisting and retrieving state in a non blocking way.

The `kv` store is persisted to the directory configured in `config.dir`. If it doesnt exist, it will be created.

Example:
```yaml
  - id: kv
    type: kv
    linked: true     # this needs to be true
    codec: json
    config:
      dir: "temp/kv" # directory to store data in
```

One response event is sent for every command in the handled event. On success to the `out` port, in the error case (invalid format or error during kv operation) to the `err` port.
Each response event will have the following metadata structure:

```js
{
  "kv": {
    "op": "<string>|null" // contains the command key that was used to trigger this response, can be `null` for error events.
  }
}

Events sent to the KV offramp contain commands. The following are supported:

#### get

Fetches the data for a given key.

**Request**:
```js
{"get": {"key": "<string|binary>"}}
```

**Response**:

Key was found, the format of decoded depends on the codec (does NOT have to be a string):
```js
{
  "ok": {
    "key": "<binary>",
    "value": "<decoded>"
  }
}
```

Key was not found:

```js
{
  "ok": {
    "key": "<binary>",
    "value": null
  }
}
```

#### put

Writes a value to a key, returns the old value if there was any.

**Request**:
```js
{
  "put": {
    "key": "<string|binary>",
    "value": "<to encode>" // the format of value depends on the codec (does NOT have to be a string)
  }
}
```

**Response**:

Key was used before, this is the old value, the format of decoded depends on the codec (does NOT have to be a string):
```js
{
  "ok": {
    "key": "<binary>",
    "value": "<decoded>"
  }
}
```

Key was not used before:
```js
{
  "ok": {
    "key": "<binary>",
    "value": null
  }
}
```

#### delete

Deletes a key, returns the old value if there was any.

**Request**:
```js
{"delete": {"key": "<string|binary>"}}
```

**Response**:

Key was used before, this is the old value, the format of decoded depends on the codec (does NOT have to be a string):

```js
{
  "ok": {
    "key": "<binary>",
    "value": "<decoded>"
  }
}
```

Key was not used before:

```js
{
  "ok": {
    "key": "<binary>",
    "value": null
  }
}
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
{
  "ok": [
    {
      "key": "<binary>", // keys are ALWAYS encoded as binary since we don't know if it's a string or binary
      "value": "<decoded>" // the value, the format of decoded depends on the codec (does NOT have to be a string)
    } // repeated, may be empty
  ]
}
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
On success:

```js
{
  "ok": null,
  "key": "<binary>"
}
```

On failure:

```js
{
  "error": {
    "current": "<decoded>", // the value that is currently stored, the format of decoded depends on the codec (does NOT have to be a string)
    "proposed": "<decoded>" // the value that was proposed/expected to be there, the format of decoded depends on the codec (does NOT have to be a string)
  },
  "key": "<binary>"
}
```

### nats
The `nats` offramp connects to Nats server(s) and publishes a message to specified subject for every event.

The default [codec](codecs.md#json) is `json`.

Supported configuration operations are:

- `hosts` - List of hosts to connect to.
- `subject` - Subject for the message to be published.
- `reply` - Optional string specifying the reply subject.
- `headers` - Option key-value pairs, specifying message headers, where the key is a string and the value is a list of strings.
- `options` - Optional struct, which can be used to customize the connection to the server (see [`nats.rs` configuration options](https://docs.rs/nats/0.9.8/nats/struct.Options.html) for more info):

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

Used metadata variables are:

- `$nats`: Record consisting of the following metadata:

    - `$reply`: Overrides `config.reply` if present.
    - `$headers`: Overrides `config.headers` if present.

Example:
```yaml
offramp:
  - id: nats-out
    type: nats
    config:
      hosts:
        - "127.0.0.1:4444"
      subject: demo
      reply: ghost
      headers:
        snot:
          - badger
          - ferris
      options:
        name: nats-demo
        reconnect_buffer_size: 1
```

### newrelic

Send events to [New Relic](https://newrelic.com/) platform, using its log apis (variable by region).

This offramp encodes events as json, as this is required by the `newrelic` log api. Postprocessors are not used.

Supported configuration options are:

- `license_key` - New Relic's license (or insert only) key
- `compress_logs` - Whether logs should be compressed before sending to New Relic  (avoids extra egress costs but at the cost of more cpu usage by tremor) (default: false)
- `region` - Region to use to send logs. Available choices: USA, Europe (default: USA)

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

### otel

CNCF OpenTelemetry offramp. Publishes to the specified host or IP and destination TCP port via gRPC messages
conforming to the CNCF OpenTelemetry protocol specification v1. Forwards tremor value variants of `logs`, `trace`
and `metrics` messages from tremor query pipelines downstream to remote OpenTelemetry endpoints.

!!! note

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
for lossless recovery. For events marked as transactional that are explicitly acknowledged, `fail` insights are propagated for events that
are not succesfully transmitted downstream. Non-transactional events ( those not marked as transactional ) are delivered on a best effort
basis. Regardless of the transaction configuration, when paired with qos operators upstream pipelines, the sink will coordinate failover
and recovery to the configured retention, replaying the retained messages upon recovery of network accessibility of the downstream endpoints.

For best effort delivery - the `qos::wal` can be omitted and events distributed when downstream endpoints are inaccessible will be
lost.

Example:

```yaml
offramp:
  - id: otlp
    type: otel
    codec: json
    config:
      port: 4317
      host: 10.0.2.1
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
- `auth` - Provide a token that will authenticate the offramp client. Supports empty string and `gcp` (default: `""`)

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

If the event data (after codec and postprocessing) is not a valid UTF8 string (e.g. if it is binary data) if will by default output the bytes with debug formatting.
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

If the event data (after codec and postprocessing) is not a valid UTF8 string (e.g. if it is binary data) if will by default output the bytes with debug formatting.
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

This connects on a specified port for distributing outbound TCP data. TLS is supported via [rustls](https://github.com/ctz/rustls).

The offramp can leverage postprocessors to frame data after codecs are applied and events are forwarded
to external TCP protocol distribution endpoints.

The default [codec](codecs.md#json) is `json`.

Supported configuration options are:

- `host` - The host to advertise as
- `port` - The TCP port to listen on
- `is_non_blocking` - Is the socket configured as non-blocking ( default: false )
- `ttl` - Set the socket's time-to-live ( default: 64 )
- `is_no_delay` - Set the socket's Nagle ( delay ) algorithm to off ( default: true )
- `tls` - If set to `true` or a detailed TLS config with the keys below, will wrap the TCP socket with a TLS session. ( default: `false` )
    - `cafile` - If provided, only server certificates signed by the Certificate Authority represented by the root certificate in `cafile` are accepted. If not provided, all root certificated distributed by Mozilla via [webpki-roots](https://github.com/rustls/webpki-roots) are loaded.
    - `domain` - if provided, this will be the domain to verify the TLS certificate against. It might differ to `host`, especially if `host` is given as IP address. If not provided, the `host` config is used as domain.

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


#### TLS Support

TLS support is enabled by providing either `tls: true` or a detailed config.

When providing `tls: true`, the TCP offramp is verifying the server it connects to and its certificate against the `host` config, and a set of common root-certificates provided by Mozilla via [webpki-roots](https://github.com/rustls/webpki-roots):

```yaml
offramp:
  - id: tcp
    type: tcp
    codec: json
    postprocessors:
      - length-prefixed
    config:
      host: "example.com"
      port: 443
      tls: true
```

This behaviour can be tuned by providing a detailed config. If `tls.cafile` is provided, the TCP offramp will only accept server certificates signed (directly or indirectly via a server-provided certificate chain) by the given root-certificate. This is useful for testing against self-signed certificates. In this case the self signed certificate needs to provided via `tls.cafile`. If `tls.domain` is provided, this value will be used instead of the `host` config to verify the domain name provided in the server certificate. This is especially useful if an IP address is used as `host` config.

Client certificates are not supported.

Example:

```yaml
offramp:
  - id: tls
    type: tcp
    codec: json
    config:
      host: "127.0.0.1"
      port: 65535
      tls:
        cafile: "path/to/custom_ca.pem"
        domain: "localhost"
```

For testing purposes, self-signed certificates need the Subject Alternative Name extension, otherwise setting up the onramp will fail with a `BadDER` Error. Adding this when generating a self-signed certificate can be done by passing `-addext 'subjectAltName = DNS:<DOMAIN>'` via `openssl` command line or by adding it to `openssl.cfg` as described in the [openssl manual](https://www.openssl.org/docs/man1.1.1/man5/x509v3_config.html#Subject-Alternative-Name).


### udp

The UDP offramp sends data to a given host and port as UDP datagram.

The default [codec](codecs.md#json) is `json`.

When the UDP onramp gets a batch of messages it will send each element of the batch as a distinct UDP datagram.

Supported configuration options are:

- `bind.host` - the local host to send data from
- `bind.port` - the local port to send data from
- `host` - the destination host to send data to
- `port` - the destination port to send data to.

!!! warn

    Setting `bound` to `false` makes the UDP offramp potentially extremely slow as it forces a lookup of the destination on each event!

Used metadata variables:

 - `$udp.host`: This overwrites the configured destination host for this event. Expects a string.
 - `$udp.port`: This overwrites the configured destination port for this event. Expects an integer.

!!! warn

    Be careful to set `$udp.host` to an IP, **not** a DNS name or the OS will resolve it on every event, which will be extremely slow!

Example:

```yaml
offramp:
  - id: udp-out
    type: udp
    postprocessors:
      - base64
    config:
      bind:
        host: "10.11.12.13"
        port: 1234
      host: "20.21.22.23"
      port: 2345
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

- `$binary` - `true` if the WebSocket message reply came as binary (`false` otherwise)

When used as a linked offramp, batched events are rejected by the offramp.

Example:

```yaml
onramp:
  - id: ws
    type: ws
    config:
      url: "ws://localhost:1234"
```

