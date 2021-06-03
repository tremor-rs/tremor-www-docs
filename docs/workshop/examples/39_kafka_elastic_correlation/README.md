# Ingesting documents from kafka into elastic

!!! note

    All the application code here is available from the docs [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/39_kafka_elastic_correlation).

This example tries to show how to use tremor as the orchestrator for ingesting documents coming from kafka into elasticsearch and notify the upstream system of success or failure of the ingest operation for every single document.

## Environment

In this walkthrough we explore how to make use of _Linked Transports_, _Guaranteed Delivery_ and _Correlation_ features of tremor.

In the `tremor_in` directory we have set up a tremor instance that acts as our data source for this workshop. It is not our main focus, but lets look at it, so we understand our source data.

### Data source

The tremor instance used for feeding data into our main system contains of a `metronome` onramp which will emit an event every second. The connected pipeline will enrich those events with some metadata destined for the kafka offramp it is connected to.
Based on random choice it will change the event format to some incompatible format. This is done so we can trigger errors at elasticsearch later on.

The script responsible for creating the events is the following:

```tremor
define script add_meta
script

  use tremor::system;
  use std::random;
  # we add a message id as kafka header,
  # that we use later on for correlation and notifying purposes
  let message_id = "#{system::ingest_ns()}";
  let $kafka = {
    "headers": {
      "message_id": message_id
    },
    "key": message_id
  };

  # trigger some errors due to invalid formats
  # ES auto creates an index schema for the first event it rerceives,
  # some next event will have a differently typed payload for the field `might_be_invalid`
  match random::bool() of
    case true => {
      "event": event,
      "might_be_invalid": [true, false]
    }
    default => {
      "event": event,
      "might_be_invalid": 2
    }
  end
end;
```

Here we switch the value of the `might_be_invalid` field, based on ramdomness.
We also create a `message_id` from the event ingest timestamp and put it into the kafka headers. We are going to need this `message_id` later on for reporting the ingestion success or failure.

The resulting event is then put to kafka into the `tremor` topic.

### Ingestion from Kafka to Elasticsearch

In our ingestion pipeline in the `tremor_out` directory, we have setup a kafka consumer consuming from the `tremor` topic. It is forwarding the messages to elasticsearch:

```tremor
define script add_correlation
script
  use tremor::origin;
  use tremor::system;
  use std::string;

  # add correlation
  let $correlation = match $kafka.headers of
    case headers = %{ present message_id } =>
      headers["message_id"]
    default =>
      # stupid fallback, actually should never happen
      "#{ system::ingest_ns() }"
  end;

  # add elastic metadata
  let $elastic = {
    "_index": "foo",
    "_id": string::from_utf8_lossy($kafka["key"])
  };

  # form the event
  {
    "event": event,
    "some_data": [ origin::as_uri_string() ]
  }
end;
```

Here we add metadata for elasticsearch, so it ends up in the right index, we use the kafka key as elastic document id.
We also extract a `message_id` from the kafka headers and put it in `$correlation`. This special metadata value will
be forwarded across linked transports, like elasticsearch.

Further down in the ingestion pipeline we batch events up into counts of 10 to be more efficient when sending stuff over to elastic.

The elasticsearch offramp will issue success and error events from its `out` and `err` ports respectively. One event per batched document or one error event if something went wrong with the overall request execution (e.g. elasticsearch is not reachable).

We handle those events in two different pipelines. Success events are handled in this one:

```tremor
define script correlate
script

  # add kafka metadata
  let $kafka = {
    "headers": {
      "message_id": $correlation
    },
    "key": $correlation
  };

  # build up the notify event for success
  {
    "success": event.success,
    "message_id": $correlation,
    "payload": event.payload,
    "elastic_metadata": $elastic
  }

end;

create script correlate;

select event from in into correlate;
select event from correlate into out;
select event from correlate/err into err;
```

Here we extract the `$correlation` metadata and put it into the event payload. The actual event is sent back to kafka into the topic: `ingest_notify`. The machinery outside of this tremor application can re-inject the message based on the reported status, if need be. For you to enjoy events flying by we also directed the events to stdout/stderr.

For handling errors we also get `$correlation` metadata and can forward it back to kafka:

```tremor
# handle elastic response from failing document or failing bulk insert
# so this might be scoped to a document or to a failing elastic bulk request
define script error_notify
script

  # add kafka metadata
  let $kafka = {
    "headers": {
      "message_id": $correlation
    },
    "key": $correlation
  };

  match $ of
    case %{ present elastic } =>
      # this is an error for an invalid event
      emit {
        "success": false,
        "message_id": $correlation,
        "payload": event.payload,
        "error": event.error,
        "elastic_metadata": $elastic
      } => "out"
    default =>
      # this is an error report regarding the bulk request to ES
      # we know it is batched, so $correlation is an array
      # we need to explode this event into 1 event per $correlation value,
      # so the reporting back to kafka has 1 kafka record per ingested document
      emit event => "explode"
  end;
end;

create script error_notify;

select event from in into error_notify;
select event from error_notify/out into out;
# explode the event for each `$correlation` value
select {
  "success": false,
  "message_id": group[0],
  "payload": event.payload,
  "error": event.error
} from error_notify/explode group by each($correlation) into out;

select event from error_notify/err into err;
```

Here we distinguish between errors per document (e.g. invalid format for the given index) and errors scoped to the whole request execution (no `$elastic` metadata).
In the case of a request error, we have an array of all the batched `$correlation` values and need to "explode" the event into 1 per `$correlation` id, so we can correctly
report back to kafka 1 document at a time.


## Trying this at home

```sh
docker compose up
```

Once everything is set up you will see logs like this in your console:

```
tremor_out_1     | [ERR] {"success":false,"message_id":"MTYyMDEzNjg1NDY2NzI5OTQwMA==","payload":{"event":{"event":{"onramp":"metronome","ingest_ns":1620136854667292300,"id":601},"might_be_invalid":2},"some_data":["tremor-kafka://kafka:9092/tremor/0/601"]},"error":{"caused_by":{"reason":"Current token (VALUE_NUMBER_INT) not of boolean type\n at [Source: (byte[])\"POST /_bulk HTTP/1.1\r\ncontent-type: application/json\r\ncontent-length: 2216\r\nuser-agent: reqwest/0.9.24\r\naccept: */*\r\naccept-encoding: gzip\r\nhost: elasticsearch:9200\r\n\r\n{\"index\":{\"_index\":\"foo\",\"_id\":\"1620136845697865700\"}}\n{\"event\":{\"event\":{\"onramp\":\"metronome\",\"ingest_ns\":1620136845697859400,\"id\":592},\"might_be_invalid\":[true,false]},\"some_data\":[\"tremor-kafka://kafka:9092/tremor/0/592\"]}\n{\"index\":{\"_index\":\"foo\",\"_id\":\"1620136846698130900\"}}\n{\"event\":{\"event\":{\"onramp\":\"metronome\",\"ingest_ns\"\"[truncated 1884 bytes]; line: 1, column: 103]","type":"json_parse_exception"},"reason":"failed to parse field [event.might_be_invalid] of type [boolean] in document with id '1620136854667299400'. Preview of field's value: '2'","type":"mapper_parsing_exception"},"elastic_metadata":{"_id":"1620136854667299400","_index":"foo","_type":"_doc","id":"1620136854667299400","index":"foo","doc_type":"_doc"}}
tremor_out_1     | [OK] {"success":true,"message_id":"MTYyMDEzNjg1MjY2NjgxMzAwMA==","payload":{"event":{"event":{"onramp":"metronome","ingest_ns":1620136852666806400,"id":599},"might_be_invalid":[true,false]},"some_data":["tremor-kafka://kafka:9092/tremor/0/599"]},"elastic_metadata":{"_id":"1620136852666813000","_index":"foo","_type":"_doc","id":"1620136852666813000","index":"foo","doc_type":"_doc","version":1}}
tremor_out_1     | [OK] {"success":true,"message_id":"MTYyMDEzNjg1MzY2NzA5NjAwMA==","payload":{"event":{"event":{"onramp":"metronome","ingest_ns":1620136853667088800,"id":600},"might_be_invalid":[true,false]},"some_data":["tremor-kafka://kafka:9092/tremor/0/600"]},"elastic_metadata":{"_id":"1620136853667096000","_index":"foo","_type":"_doc","id":"1620136853667096000","index":"foo","doc_type":"_doc","version":1}}
```

Here we see one error message and two successful messages. For the error message you can clearly recognize the cause: `Current token (VALUE_NUMBER_INT) not of boolean type`.