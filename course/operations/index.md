<!-- .slide: data-background="#333333" -->

## Operations and Development

- Installation & Deployment
- Configuration
- Pipeline Development
- Example use cases
- Monitoring
- Performance Tuning

---

## Installation

__Docker:__

```bash

 docker pull tremorproject/tremor:latest
 docker run tremorproject/tremor:latest

```

---

## Installation

__From source:__

1. [Install Requirements](https://docs.tremor.rs/development/quick-start/#without-docker)
2. Compile the `tremor` binary:

```bash

 cargo build --release --all --verbose
 

```

>>>

## Starting Tremor

One binary to rule them all:

* [tremor](https://docs.tremor.rs/operations/cli/)

---

## Starting Tremor

Start a naked tremor instance:

```bash

 tremor server run

```

---

## Starting Tremor

Start tremor and deploy provided static artefacts:

```bash

 tremor server run -f pipeline.trickle -f artefacts.yaml

```

>>>

## Repositories and Artefacts

- Tremor is made out of building blocks you can publish, connect and instantiate independently
- Artefacts are configurations that are available and addressable within tremor
  - [Sources](https://docs.tremor.rs/artefacts/onramps/)
  - [Sinks](https://docs.tremor.rs/artefacts/offramps/)
  - [Pipelines](https://docs.tremor.rs/tremor-query/)
  - [Bindings](https://docs.tremor.rs/operations/configuration-walkthrough/#write-a-binding-specification) (connections of the three former artefacts)

---

## Repositories and Artefacts

- Artefacts are published into the repository:

```yaml
# onramp.yaml
id: my-onramp
type: file
preprocessors:
  - lines
config:
  source: "/var/log/mail.log"
```

```bash
tremor server run -f onramp.yaml
```

---

## Repositories and Artefacts

- Artefacts are available for creation
- Fully deploying a connected pipeline is a 2-step process

---

## Bindings

- Onramps, pipelines, offramps are connected via binding artefacts
- can be templates, interpolated:

```yaml

 id: my-binding
 links:
   '/onramp/onramp-artefact-id/{instance}/out': ['/pipeline/my-pipeline/{instance}/in']
   '/pipeline/my-pipeline/{instance}/out': ['/offramp/offramp-artefact-id/{instance}/in']

```

>>>

## Registry and Instances

- Connected pipelines are instantiated/started by instantiating a binding
- filling in the missing interpolations

```yaml
 mapping:
   instance_01:
     instance: "01"
   instance_02:
     instance: "02"

```

---

# Registry and Instances

- for each referenced artefact an instance is created (if necessary)
- instances live in the registry
- binding instances represent connected event flows
- runtime starts artefacts and events can flow

>>>

## Changing Configuration at Runtime

- via [REST API](https://docs.tremor.rs/api/)
- publishing artefacts
- creating instances

```bash

 $ curl -X POST -H "Content-Type: application/yaml" --data-binary @metronome-onramp.yaml http://localhost:9898/onramp
 {
   "id":"ws",
   "type":"rest",
   "description":"",
   "linked":false,
   "codec":"string",
   "config":{
     "host":"127.0.0.1",
     "port":8080
   }
 }
```

---

## Changing Configuration at Runtime

- Bindings can only be deleted and redeployed, not changed dynamically

>>>

## Pipeline Development

- [tremor language server](https://github.com/tremor-rs/tremor-language-server):
- [VS Code extension](https://marketplace.visualstudio.com/items?itemName=tremorproject.tremor-language-features
- [VIM plugin](https://github.com/tremor-rs/tremor-vim) (There are no other valid editors!)

---

## Look ma, no YAML! (almost)

- Proper language means:
  - powerful parser/interpreter
  - helpful errors beyond syntax
  - more expressive
  - IDE support

--- 

## Quick Iterative Testing

Example Pipeline

```trickle
# example.trickle
define script example
script
  match event of
    case %{ "not_a_badger": true } => emit event
    default =>
      let event["snot"] = "badger"
  end;
  event;
end;

create script example;

select event from in into example;
select from example into out;
```

---

## Quick Iterative Testing

```bash
 $ tremor run example.trickle
 Error: 
    2 | script
    3 |   match event of
    4 |     case %{ "not_a_badger" == true } => emit event
      |             ^ Found the token `"` but expected one of `<ident>`, `absent`, `present`, `}`
      |               NOTE: Did you mean to use `}`?
    5 |     default =>
    6 |       let event["snot"] = "badger"
```

Nice!
---

---

## Quick Iterative Testing

```trickle

## Reliability

Tremor is in continuous production for 2 years, with expanding use cases
that span logging, metrics, data technologies  and kubernetes domains with
a small core development team. Tremor has never had a serious incident in
production.

---

## Productivity

Tremor replaces a eclectic range of in-house, commercial off the shelf and
open source single purpose data transformation, processing and distribution
infrastructure with a single, easier to operate solution designed for very
high usability in at scale production environments

---

## UX

Tremor has good UX. It doesnt <b>SUX</b> in many ways:

- It doesn't barf stacktraces
- It doesn't barf nested stacktraces
- You don't program it in YAML ( not 100% true yet )
- Tremor won't panic in production
- Tremor is built in a safe programming language ( mostly )

>>>


### Architecture Overview

A high level overview of tremor-based systems architecture

---

### Tremor Nodes

![Tremor Node High Level Architecture](./assets/hla.png)

---

### Core concepts

- Sources. Ingest data from the outside world ( onramps )
- Sinks. Contribute data to the outside world ( offramps )
- Linked Transports. Have `source` and `sink` natures
- Pipelines. Business logic compiles to an event flow DAG

>>>

### Sources

- Can be a connector that consumes data via poll.
- Can be a connector that exposes a messaging consumer endpoint.
- Implemented in the rust programming language.
- Configured in YAML

---

```yaml
  - id: postgres-input
    type: postgres          # Use postgres/timescale connector
    codec: json             # Specify data format as json
    config:
      host: postgres        # Domain hostname
      port: 5432            # TCP port
      user: postgres        # Username
      password: example     # Password
      dbname: products      # Database
      interval_ms: 10000    # Polling interval ( 10 seconds )
      query: "SELECT * FROM transactions WHERE created_at >= $1 AND created_at < $2;"
      consume_from: "2019-12-01 00:00:00.000000 +00:00"
      cache:
        path: "/etc/tremor/cache.json"      # Track continuation/resume point
        size: 4096                          # Retention ( number of documents )
```

<div style='font-size: 20px'>TimescaleDB source ( periodic polling )</div>

---

```yaml
  - id: crononome-input
    type: crononome
    codec: json
    config:
      entries:
        - name: 5s                 # label
          expr: "0/5 * * * * *"    # cron-like schedule specification
          payload:                 # payload data
            user_id:
              fieldType: "INT8"
              name: "user_id"
              value: 12345
            product_id:
              fieldType: "VARCHAR"
              name: "product_id"
              value: jdwa2djh2
            quantity:
              fieldType: "INT8"
              name: "quantity"
              value: 2
            created_at:
              fieldType: "TIMESTAMPTZ"
              name: "created_at"
              value: "2020-04-08 00:00:00.000000 +00:00"
```

<div style='font-size: 20px'>Cron-like scheduled events</div>

>>>

### Sinks

- Can be a connector that publishes data via RPC.
- Can be a connector that exposes a messaging publicationendpoint.
- Implemented in the rust programming language.
- Configured in YAML

---

```yaml
  - id: timescaledb-output
    type: postgres
    codec: json
    config:
      host: timescaledb
      port: 5432
      user: postgres
      password: example
      dbname: measurements
      table: events
```

<div style='font-size: 20px'>Postgres database sink ( event driven persistence )</div>

---

```yaml
  - id: debug
    type: stdout
    codec: json
```


<div style='font-size: 20px'>Development convenience for interactive debugging</div>

>>>

### Pipelines

- Business logic is implemented in tremor-query
- Tremor query embeds tremor-script - a functional expression language
- Tremor query compiles to an event Pipeline Directed-Acyclic-Graph
- The tremor runtime manages source, sink, peer and pipeline lifecycle

---

```trickle
# postgres -> timescale
select event from in into out;
```
<div style='font-size: 20px'>Poll postgres very 10seconds for updates</div>

<br/>

```trickle
# cron -> timescale
select event.trigger.payload into out;
```
<div style='font-size: 20px'>Periodic events via cron every 10 seconds</div>

---

### Deployment Logic

```yaml
binding:
  - id: app-template
    links:
      '/onramp/postgres-input/{instance}/out': [ '/pipeline/measure-pg/{instance}/in' ]
      '/onramp/crononome-input/{instance}/out': [ '/pipeline/measure-cron/{instance}/in' ]
      '/pipeline/measure-pg/{instance}/out': [ '/offramp/timescale/{instance}/in', '/offramp/system::stdout/{instance}/in' ]
      '/pipeline/measure-cron/{instance}/out': [ '/offramp/timescale/{instance}/in', '/offramp/system::stdout/{instance}/in' ]
mapping:
  /binding/app-template/my-instance:
    instance: 'my-instance'
```

```shell
tremor server run
  -f postgres.trickle cron.trickle  \ # logic
    postgres.yaml cron.yaml         \ # sources
    timescale.yaml                  \ # sinks
    instance.yaml                   \ # instances
```

---

### Deployment diagram

![Timescale Example Deployment](./assets/timescale-example.png)

>>>

### Peers

- Associates sources and sinks
- Enables bridging, load balancing and routing RPC protocols
- Allows request and response flows to be implemented in event logic
- Allows service control and data abstractions to be adapted to event logic

---

![Peer Example](./assets/peer-example.png)

---

```yaml
onramp:
  - id: http
    type: rest
    linked: true    # enable linked peering
    codec: string
    config:
      host: 0.0.0.0
      port: 8139
```

---

```yaml
binding:
  - id: main
    links:
      "/onramp/http/{instance}/out":
        ["/pipeline/request_processing/{instance}/in"]

      # process incoming requests and send back the response
      "/pipeline/request_processing/{instance}/out":
        ["/onramp/http/{instance}/in"]

  - id: error
    links:
      "/onramp/http/{instance}/err":
        ["/pipeline/internal_error_processing/{instance}/in"]

      "/pipeline/request_processing/{instance}/err":
        ["/pipeline/internal_error_processing/{instance}/in"]

      # send back errors as response as well
      "/pipeline/internal_error_processing/{instance}/out":
        ["/onramp/http/{instance}/in"]

      # respond on errors during error processing too
      "/pipeline/internal_error_processing/{instance}/err":
        ["/onramp/http/{instance}/in"]
```

---

```trickle
define script process
script
  # embed tremor-script logic ... our API implementation
end;
create script process;

# request handling loop
select event from in into process;
select event from process into out;

# logical request processing errors -> logical error responses
select event from process/app_error into out;

# tremor runtime errors -> internal server error
select event from process/err into err;
```

---

```trickle
 # handlers
  match $request.url.path of
    # echo handler
    case "/echo" =>
      emit {
        "body": event,
        "meta": $request,
      }

    case "/ping" =>
      emit "pong {ingest_ns()}"

    # ...
```

>>>

### API

- The tremor API is used for monitoring, deployment and administration
- Publish, find and bind sources, sinks, pipelines
- Sources and Sinks are automatically removed upon quiescence
- Connect sources to pipelines
- Connect pipelines to sinks

---

- [API documentation](https://docs.tremor.rs/api/)
- [API cli](https://docs.tremor.rs/operations/cli/#api)


<div style='font-size: 20px'>You can proxy the API using linked transports</div>

>>>

### Solutions

<div style='font-size: 20px'>
In this section we look at some examples of existing production
solutions based on tremor.
</div>

<br/>

---

### Wayfair Platform Logging Service

![Basic Logging Architecture](./assets/logging-arch-basic.png)
<div style='font-size: 20px'>A simplified high level view of logging systems architecture at Wayfair</div>


---

### Possible Target Logging Architecture

![Target Logging Architecture](./assets/logging-arch-next-maybe.png)
<div style='font-size: 20px'>A simplified high level view of one potential future logging systems architecture at Wayfair. Moving the transformation tier logic upstream to the source tiers allows greater flexibility, reduced traffic volumetric, and reduces deployment footprint and associated costs. Tremor as a sidecar is already in production in Kubernetes use cases</div>

---

### Aggregation and Metrics

![Aggregation of Metrics](./assets/metrics-arch-basic.png)

<div style='font-size: 20px'>Source tier collects metrics and partitions measures into partitions. Partitions are streamed to the aggregation tier with partition affinity. Aggregation tier summarises and forwards to distribution tier for downstream consumers.</div>

---

### Static Partitioning

```trickle
define script distribute
with
  hosts = ["g1", "g2", "g3"]
script
  use tremor::chash;
  let g = event.tags["__TREMOR_GROUP__"];
  let event.tags = patch event.tags of
    erase "__TREMOR_GROUP__"
  end;
  match args.hosts[chash::jump(g, array::len(args.hosts))] of
    case "g1" => emit => "g1"
    case "g2" => emit => "g2"
    case "g3" => emit => "g3"
    default => emit => "err"
  end
end;

create script distribute;

select
  patch event of
    update "fields" => { "{group[2]}": event.fields[group[2]] },
    merge "tags" => { "__TREMOR_GROUP__": group[3] }
  end
from in
group by set(event.measurement, event.tags, each(record::keys(event.fields)))
into distribute;

select event from distribute/error into err;
select event from distribute/g1 into out/g1;
select event from distribute/g2 into out/g2;
select event from distribute/g3 into out/g3;
```

---

### Aggregator

```trickle
define tumbling window `10secs`
with
   interval = datetime::with_seconds(10),
end;
define tumbling window `1min`
with
   interval = datetime::with_minutes(1),
end;
define tumbling window `10min`
with
   interval = datetime::with_minutes(10),
end;
define tumbling window `1h`
with
   interval = datetime::with_hours(1),
end;

define generic::batch operator batch
with
  count = 8000,
  timeout = 10000
end;
create operator batch;

select {
    "measurement": event.measurement,
    "tags": patch event.tags of insert "window" => window end,
    "stats": stats::hdr(event.fields[group[2]], [ "0.5", "0.9", "0.99", "0.999" ]),
    "class": group[2],
    "timestamp": win::first(event.timestamp), # snot
}
from in[`10secs`, `1min`, `10min`, `1h`]
where event.measurement == "udp_lb_test"
   or event.measurement == "kafka-proxy.endpoints"
   or event.measurement == "burrow_group"
   or event.measurement == "burrow_partition"
   or event.measurement == "burrow_topic"
group by set(event.measurement, event.tags, each(record::keys(event.fields)))
into normalize;

create stream normalize;

select {
  "measurement":  event.measurement,
  "tags":  event.tags,
  "timestamp": event.timestamp, #asdf
  "fields":  {
    "count_{event.class}":  event.stats.count, # "
    "min_{event.class}":  event.stats.min,
    "max_{event.class}":  event.stats.max,
    "mean_{event.class}":  event.stats.mean,
    "stdev_{event.class}":  event.stats.stdev,
    "var_{event.class}":  event.stats.var,
    "p50_{event.class}":  event.stats.percentiles["0.5"],
    "p90_{event.class}":  event.stats.percentiles["0.9"],
    "p99_{event.class}":  event.stats.percentiles["0.99"], 
    "p99.9_{event.class}":  event.stats.percentiles["0.999"]
  }
}
from normalize
into batch;

select event from batch into out;

```

---

### Alerting via Alerta Integration

```trickle
# A 2019 berlin hackathon entry by Ernad Halilovic ( cyclopes )

# normalize
let severity = match event of
  case %{ status == 0 } => "ok"
  case %{ status == 1 } => "warning"
  case %{ status == 2 } => "critical"
  default => "ok"
end;

# Alert to be sent to alerta ( uses http/rest sink )
{
  "attributes": {
    "region": "bo1"
  },
  "correlate": [ "ReplicationError", "ReplicationOK" ],
    "environment": "Production",
    "event": "ReplicationError",
    "group": "Infra",
    "origin": "tremor",
    "resource": "githubc1n1.host.bo1.csnzoo.com",
    "service": [ "github" ],
    "severity": severity,
    "tags": [ "releng" ],
    "text": "Github replication is problematic.",
    "type": "tremorAlert",
    "value": ""
}
```
---

### AI - Twitter Sentiment Analysis

```trickle
# A 2020 berlin hackaton entry by Christian Rehm et al

define bert::summarization operator s # Bert NLP operator
with
  file = "bla"
end;

define script process
script
  use std::string;
  {
      "summary": $summary,
      "text": string::replace(event, "\n", " ")
  }
end;

create operator s;
create script process;

select event from in into s;
select event from s into process;
select event from process into out;%
```

---

### A distributed configuration micro-service

- [Configurator](https://docs.tremor.rs/workshop/examples/37_configurator/)
- [Quota Service](https://docs.tremor.rs/workshop/examples/36_quota_service/)

<div>From `v0.9` tremor can now be used to quickly build and deploy micro-services</div>

>>>

### New in v0.9 ( `Experimental` )

- Circuit breakers. Finer grained QoS
- Linked Transports. Enable event-sourced micro-services
- Task-based concurrency. Deploy 1000's of pipelines in 1 tremor node.

>>>


### Next major release

- Raft-based consensus mechanism and K/V storage
- Ring based cluster topology
- Riak-style V-Nodes
- Tremor cluster-aware network protocol


>>>

### Further reading

- [WWW](https://www.tremor.rs)
- [Docs](https://docs.tremor.rs)
- [Rfcs](https://rfcs.tremor.rs)
- [CNCF Landscape](https://landscape.cncf.io/selected=tremor)
- [Twitter](https://twitter.com/tremordebs)

>>>

### End of `overview` guide
<!-- .slide: data-background="#33FF77" -->

This is the end of the overview

Note: This will only appear in speaker notes window
