# syslog udp dns

This workshop is the samne as the [syslog_upd](../14_syslog_udp/) workship with the added component of enriching the syslog message we receive with a DNS lookup.

We will only discuss the newly introduced components, for the rest pleas refer to the [syslog_upd](../14_syslog_udp/) workshop.

## Setup

!!! tip
All the code here is available in the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/14_syslog_udp) as well and can be run with `docker compose up`.

## Environment

We get a new [sink](etc/tremor/config/00_ramps.yaml), the `dns` sink. This is what tremor calls a `linked transport`, aka a `sink` or `source` that can both receive and send messages.

In the case of the `dns` sink it receives lookup requests and sends the replies.

This changes the [binding](./etc/tremor/config/01_binding.yaml) the following way:

```
metronome -> producer -> syslog-udp-out

syslog-udp-in -> dns -> dns

dns -> consumer -> stdout-output
```

## Business Logic

The `producer` pipeline remains unchanged however we add a new `dns` pipeline and the `consumer` piepline now includes some logic.

The `dns` pipeline does two things. First it moves the event itself into the `$correlation` metadata. Linked transports will preserve this metadata key over requests allowing to correlate the output event with the input request. Second it changes the event into a lookup of the `A` record (ip address) for the hostname. Finally we do the wiering with select statments.

!!! warn
    Storing data in `$correlation` will mean this data has to be kept in memory until the event is processed, depending on throughput and pending requests this can be a significant memory cost.

```trickle
# dns.trickle
define script dns
script
 let $correlation = event;
 {
  "lookup": $correlation.hostname,
  "type": "A"
 }
end;

create script dns;

select event from in into dns;
select event from dns into out;
```

In addition the `consumer` pipeline got slightly more complicated. We use `merge` to replace the lookup response from the `dns` sink with it's correlation (the orriginal event) and merge merge it by inserting the IP we looked up into the event. In result we now have the original event with the added `ip` field containing the IP correlating to the hostname.

```trickle
# consumer.trickle
select merge $correlation of {"ip": event[0].A} end from in into out
```
