# syslog udp

The `syslog udp` example is demonstrate a number things:

1. Encoding data in the `syslog` format.
2. Sending data over `UDP`.
3. Receiving data over `UDP`.
4. Decoding `syslog` formated data.

For easy digestion it is entirely selfcontained inside a singel tremor instance using multiple paralell pipelines, sinks and sources.

## Setup

!!! tip
    All the code here is available in the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/14_syslog_udp) as well and can be run with `docker compose up`.

## Environment

The [sources and sinks](etc/tremor/config/00_ramps.yaml) we use are:

- The `metronome` source - to generate data in one second intervals.
- The `udp` sink - to send the data over `UDP`.
- The `udp` source - to receive data via `UDP`.
- The `stdout` sink - to display data decoded and re-formated as `JSON`.

In addition we have two pipelines.

The [producer](etc/tremor/config/consumer.trickle) pipeline takes the tick from metronome and generates a syslog message. It is only handling message rewriting.

The [consumer](etc/tremor/config/consumer.trickle) pipeline takes the syslog message and forwards it. It is a passthrough pipeline.

The [binding](./etc/tremor/config/01_binding.yaml) expresses those relations and gives the graph of onramp, pipeline and offramp. We hare left with those two workflows:

```
metronome -> producer -> syslog-udp-out

syslog-udp-in -> consumer -> stdout-output
```

Finally the [mapping](./etc/tremor/config/02_mapping.yaml) instanciates the binding with the given name and instance variable to activate the elements of the binding.

## Business Logic

The only interesting part to look at is the event rewriting, this uses an example syslog message and adds the `event.id` as a `strucuted_data` field.

```trickle
select {
  "severity": "notice",
  "facility": "local4",
  "hostname": "example.com",
  "appname": "evntsog",
  "msg": "BOMAn application event log entry...",
  "procid": null,
  "msgid": "ID47",
  "protocol": "RFC5424",
  "protocol_version": 1,
  "structured_data": {
              "exampleSDID@32473" :
              [
                {"eventSource": "Tremor"},
                {"eventID": "#{ event.id }"}
              ]
            },
  "timestamp": event.ingest_ns
} from in into out
```

## Testing

from inside the docker container, custom syslog messages can be send with the `logger` command:

```bash
$ logger -d -n 127.0.0.1 -P 12201 "Weeeeh. It works :D"
```
