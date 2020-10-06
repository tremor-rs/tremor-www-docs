# Persistent Write-Ahead Log

The write-ahead log ( WAL ) builds on circuit breaker and acknowledgement mechanisms to
provide guaranteed delivery. The write-ahead log is useful in situations
where sources/onramps do not offer guaranteed delivery themselves, but the data being distributed downstream can benefit from protection against loss and duplication.

In the configuration in this tutorial we configure a persistent WAL.

## Environment

We configure a metronome as a source of data.

```yaml
# File: etc/tremor/config/metronome.yaml
onramp:
  - id: metronome
    type: metronome
    config:
      interval: 1000 # Every second
```

We configure a straight forward passthrough query to distribute
the data to connected downstream sinks.

```trickle
# File: etc/tremor/config/persistent.trickle
use tremor::system;

define qos::wal operator on_disk_wal
with
  read_count = 20,
  max_elements = 1000, # Capacity limit of 1000 stored events
  max_bytes = 10485760 # Capacity limit of 1MB of events
end;

create operator on_disk_wal;

select patch event of
  insert hostname = system::hostname()
end
from in into on_disk_wal;

select event from on_disk_wal into out;
```

We then distribute the metronome events downstream to another websocket
listener. We use websocat for this purpose in this example. We can invoke
the server as follows:

```bash
$ websocat -s 8080
Listening on ws://127.0.0.1:8080/
```

We configure the sink/offramp as follows:

```yaml
offramp:
  - id: ws
    type: ws
    config:
      url: ws://localhost:8080/
```

Finally, we interconnect the source, sink and pipeline logic into
an active flow:

```
binding:
  - id: default
    links:
      "/onramp/metronome/{instance}/out": ["/pipeline/main/{instance}/in"]
      "/pipeline/main/{instance}/out": ["/offramp/ws/{instance}/in"]

mapping:
  /binding/default/01:
    instance: "01"
```

Running the example via the tremor cli as follows:

```bash
$ tremor server run -f etc/tremor/config/*
```

# Insights

If the tremor process restarts we pick up and re-send events that have not been acknowledged by the ws offramp and then carry on with new events coming from the metronome:

```bash
$ websocat -s 8080 ; websocat -s 8080
Listening on ws://127.0.0.1:8080/
{"onramp":"metronome","id":0,"hostname":"localhost","ingest_ns":1600860720749137000}
{"onramp":"metronome","id":1,"hostname":"localhost","ingest_ns":1600860721751965000}
{"onramp":"metronome","id":2,"hostname":"localhost","ingest_ns":1600860722756684000}
{"onramp":"metronome","id":3,"hostname":"localhost","ingest_ns":1600860723761037000}
{"onramp":"metronome","id":4,"hostname":"localhost","ingest_ns":1600860724764683000}
{"onramp":"metronome","id":3,"hostname":"localhost","ingest_ns":1600860723761037000}
{"onramp":"metronome","id":4,"hostname":"localhost","ingest_ns":1600860724764683000}
{"onramp":"metronome","id":0,"hostname":"localhost","ingest_ns":1600860730353260000}
{"onramp":"metronome","id":1,"hostname":"localhost","ingest_ns":1600860731355463000}
{"onramp":"metronome","id":2,"hostname":"localhost","ingest_ns":1600860732357883000}
{"onramp":"metronome","id":3,"hostname":"localhost","ingest_ns":1600860733362429000}
{"onramp":"metronome","id":4,"hostname":"localhost","ingest_ns":1600860734364277000}
{"onramp":"metronome","id":5,"hostname":"localhost","ingest_ns":1600860735367967000}
{"onramp":"metronome","id":6,"hostname":"localhost","ingest_ns":1600860736373137000}
```

!!! note
    We restarted tremor after sending event with id `4`. It did resend events `3` and `4` as they have not been acked from the perspective of the WAL yet.

If the downstream websocket service restarts we can recover up to 1000 events or any number of events worth 1MB. We may lose in flight events that were already acknowledged at the time the server went down and thus not fully delivered by the downstream system.

```bash
$ websocat -s 8080 ; websocat -s 8080
{"onramp":"metronome","id":0,"hostname":"ALT01828","ingest_ns":1600861519788231000}
{"onramp":"metronome","id":1,"hostname":"ALT01828","ingest_ns":1600861520790241000}
{"onramp":"metronome","id":2,"hostname":"ALT01828","ingest_ns":1600861521792297000}
{"onramp":"metronome","id":3,"hostname":"ALT01828","ingest_ns":1600861522797476000}
{"onramp":"metronome","id":4,"hostname":"ALT01828","ingest_ns":1600861523802114000}
^C
$  websocat -s 8080 ; websocat -s 8080
Listening on ws://127.0.0.1:8080/
{"onramp":"metronome","id":6,"hostname":"ALT01828","ingest_ns":1600861525809835000}
{"onramp":"metronome","id":7,"hostname":"ALT01828","ingest_ns":1600861526813574000}
{"onramp":"metronome","id":8,"hostname":"ALT01828","ingest_ns":1600861527817722000}
{"onramp":"metronome","id":9,"hostname":"ALT01828","ingest_ns":1600861528822667000}
{"onramp":"metronome","id":10,"hostname":"ALT01828","ingest_ns":1600861529826521000}
{"onramp":"metronome","id":11,"hostname":"ALT01828","ingest_ns":1600861530830497000}
```

!!! note
    We killed the websocket server and restarted right afterwards. We in fact lost 1 event (id `5`) which was acked inside tremor but not yet fully delivered to the console by websocat. Other events that the offramp was unable to send will be resent once the ws offramp can connect again.

In short, the persistent in memory wal can assist with partial recovery of downstream system or tremor itself and will actively reduce data loss within the configured retention but it is not guarenteed to be lossless.
