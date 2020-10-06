# Round Robin

The roundrobin distribution demo builds from the best-effort transient guaranteed
delivery demo and adds round-robin load balancing to a fixed number of downstream
consumers.

In this configuration we build a transient in-memory WAL with round-robin load-balancing
dispatch to three downstream distribution endpoints.

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
use tremor::system;

define qos::wal operator in_memory_wal with
  read_count = 20,
  max_elements = 1000, # Capacity limit of 1000 stored events
  max_bytes = 10485760 # Capacity limit of 1MB of events
end;

define qos::roundrobin operator roundrobin
with
  outputs = [  "ws0", "ws1", "ws2" ]
end;

# create operator in_memory_wal;
create operator roundrobin;

select merge event of
  { "hostname" : system::hostname() }
end
from in into in_memory_wal;

select event from in_memory_wal into roundrobin;

select event from roundrobin/ws0 into out/ws0;
select event from roundrobin/ws1 into out/ws1;
select event from roundrobin/ws2 into out/ws2;
```

We then distribute the metronome events downstream to three
downstream websocket servers and round robin load balance
across them

Server 1, in first shell

```bash
$ websocat -s 8080
Listening on ws://127.0.0.1:8080/
```

Server 2, in second shell

```bash
$ websocat -s 8081
Listening on ws://127.0.0.1:8081/
```

Server 3, in third shell

```bash
$ websocat -s 8082
Listening on ws://127.0.0.1:8082/
```

We configure the sink/offramp instances as follows:

```yaml
offramp:
  - id: ws0
    type: ws
    config:
      url: ws://localhost:8080/
  - id: ws1
    type: ws
    config:
      url: ws://localhost:8081/
  - id: ws2
    type: ws
    config:
      url: ws://localhost:8082/
```

Finally, we interconnect the source, sink and pipeline logic into
an active flow:

```
binding:
  - id: default
    links:
      "/onramp/metronome/{instance}/out": ["/pipeline/roundrobin/{instance}/in"]
      "/pipeline/roundrobin/{instance}/ws0": [ "/offramp/ws0/{instance}/in"]
      "/pipeline/roundrobin/{instance}/ws1": [ "/offramp/ws1/{instance}/in"]
      "/pipeline/roundrobin/{instance}/ws2": [ "/offramp/ws2/{instance}/in"]

mapping:
  /binding/default/01:
    instance: "01"
```

Running the example via the tremor client as follows:

```bash
$ tremor server run -f etc/tremor/config/*
```

# Insights

If the tremor process restarts we sequence from the beginning.

```bash
$ websocat -s 8080
Listening on ws://127.0.0.1:8080/
{"onramp":"metronome","id":0,"hostname":"ALT01827",  "ingest_ns":1600689100122526000}
{"onramp":"metronome","id":3,"hostname":"ALT01827","ingest_ns":1600689101122912000}
{"onramp":"metronome","id":6,"hostname":"ALT01827", "ingest_ns":1600689102124688000}
...
```

Otherwise, we should see sequences distribute across our downstream
round-robin distribution set

If we lose a downstream instance we load-balance across the remainder

If we lose all downstream instances, we buffer up to our rentention limit of 1000 events or 1MB of event data.

!!! note
    Notice that we recover **most** but now all of the data. As the downstream websocket connection is not a guaranteed delivery connection the recovery and protection against data loss is best effort in this case

In short, the transient in memory wal can assist with partial recovery and
will actively reduce data loss to within the configured retention but it is
not lossless. We can also use redundant downstream distribution endpoints to
further insulate against catastrophic unrecoverable errors by adding the round
robin dispatch strategy and configuring multiple downstream endpoints.
