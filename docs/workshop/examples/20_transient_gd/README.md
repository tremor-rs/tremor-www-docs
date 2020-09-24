# Transient Write-Ahead Log

The write-ahead log builds on circuit breaker and acknowledgement mechanisms to
provide guaranteed delivery. The write-ahead log is useful in situations
where sources/onramps do not offer guaranteed delivery themselves, but the data being distributed downstream can benefit from protection against loss and duplication.

In the configuration in this tutorial we configure a transient in-memory WAL.

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
# File: etc/tremor/config/transient_gd.trickle
use tremor::system;

define qos::wal operator in_memory_wal
with
  read_count = 20,
  max_elements = 1000, # Capacity limit of 1000 stored events
  max_bytes = 10485760 # Capacity limit of 1MB of events
end;

create operator in_memory_wal;

select patch event of
  insert hostname = system::hostname()
end
from in into in_memory_wal;

select event from in_memory_wal into out;
```

We then distribute the metronome events downstream to another websocket
listener. We use `websocat` for this purpose in this example. We can invoke
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

Running the example via the tremor client as follows:

```bash
$ tremor server run -f etc/tremor/config/*
```

# Insights

1. If the tremor process restarts we sequence from the beginning.

> ```bash
> $ websocat -s 8080
> Listening on ws://127.0.0.1:8080/
> {"onramp":"metronome","id":0,"hostname":"ALT01827","ingest_ns":1600689100122526000}
> {"onramp":"metronome","id":1,"hostname":"ALT01827","ingest_ns":1600689101122912000}
> {"onramp":"metronome","id":2,"hostname":"ALT01827","ingest_ns":1600689102124688000}
> {"onramp":"metronome","id":0,"hostname":"ALT01827","ingest_ns":1600689104854927000}
> {"onramp":"metronome","id":1,"hostname":"ALT01827","ingest_ns":1600689105855314000}
> {"onramp":"metronome","id":2,"hostname":"ALT01827","ingest_ns":1600689106855645000}
> {"onramp":"metronome","id":3,"hostname":"ALT01827","ingest_ns":1600689107856271000}
> {"onramp":"metronome","id":0,"hostname":"ALT01827","ingest_ns":1600689202887145000}
> {"onramp":"metronome","id":1,"hostname":"ALT01827","ingest_ns":1600689203888395000}
> {"onramp":"metronome","id":2,"hostname":"ALT01827","ingest_ns":1600689204889220000}
> ```
>
> Notice that we start from sequence `0` 3 times, so we restarted tremor 3 times.

2. If the downstream websocket service restarts we can recover up to
   1000 events. We may lose in flight events that were sending at the
   time the server went down. However, for fast restarts of the downstream
   service the losses should be minimal.

> ```bash
> $ websocat -s 8080
> Listening on ws://127.0.0.1:8080/
> {"onramp":"metronome","id":17,"hostname":"ALT01827","ingest_ns":1600689219933167000}
> {"onramp":"metronome","id":18,"hostname":"ALT01827","ingest_ns":1600689220936343000}
> {"onramp":"metronome","id":19,"hostname":"ALT01827","ingest_ns":1600689221937353000}
> {"onramp":"metronome","id":20,"hostname":"ALT01827","ingest_ns":1600689222942518000}
> {"onramp":"metronome","id":21,"hostname":"ALT01827","ingest_ns":1600689223945736000}
> {"onramp":"metronome","id":22,"hostname":"ALT01827","ingest_ns":1600689224949145000}
>
> $ websocat -s 8080
> Listening on ws://127.0.0.1:8080/
> {"onramp":"metronome","id":25,"hostname":"ALT01827","ingest_ns":1600689227960081000}
> {"onramp":"metronome","id":26,"hostname":"ALT01827","ingest_ns":1600689228960247000}
> {"onramp":"metronome","id":27,"hostname":"ALT01827","ingest_ns":1600689229960449000}
> {"onramp":"metronome","id":28,"hostname":"ALT01827","ingest_ns":1600689230962355000}
> {"onramp":"metronome","id":29,"hostname":"ALT01827","ingest_ns":1600689231962934000}
>
> $ websocat -s 8080
> Listening on ws://127.0.0.1:8080/
> {"onramp":"metronome","id":31,"hostname":"ALT01827","ingest_ns":1600689233968332000}
> {"onramp":"metronome","id":32,"hostname":"ALT01827","ingest_ns":1600689234973058000}
> {"onramp":"metronome","id":33,"hostname":"ALT01827","ingest_ns":1600689235974217000}
> {"onramp":"metronome","id":34,"hostname":"ALT01827","ingest_ns":1600689236975746000}
> {"onramp":"metronome","id":35,"hostname":"ALT01827","ingest_ns":1600689237976774000}
> {"onramp":"metronome","id":36,"hostname":"ALT01827","ingest_ns":1600689238980380000}
> {"onramp":"metronome","id":37,"hostname":"ALT01827","ingest_ns":1600689239985447000}
> ```
>
> Notice that we recover **most** but now all of the data. As the downstream websocket connection is not a guaranteed delivery connection the recovery and protection against data loss is best effort in this case

In short, the transient in memory wal can assist with partial recovery and
will actively reduce data loss within the configured retention but it is
not lossless.
