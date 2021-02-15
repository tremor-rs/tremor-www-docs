<!-- .slide: data-background="#333333" -->

## Tremor Intermediate Workshop - 1

- Connecting to Kafka
- Trickle and Tremorscript
- Rate-Limiting
- Group By and Windows
- Linked Transport

---

## Lab Exercise 1

<div style='font-size: 20px'>

In this section, we will gradually build a solution for processing structures log messages
from kafka, classify and rate-limit them.
</div>

---

## Requirements

- Docker
- docker-compose

```sh
git clone git@github.com:tremor-rs/tremor-www-docs.git
cd course/intermediate-lab
```

---

## Task 0: Setup trecker

```sh
# directory where we will keep all the lab content
cd intermediate-lab

# download trecker
curl https://docs.tremor.rs/course/scripts/trecker -o trecker
chmod u+x trecker

# validate. should give cli usage
# optional: place the script somewhere in your $PATH for wider access
./trecker -h
```

---

## ✋ Task 1: Connect to kafka

__Preparation__

Start kafka and kafka_feeder:

```sh
cd kafka_feeder
docker-compose up
```

Get IP:

```sh
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' kafka_feeder_kafka_1
```

---

## ✋ Task 1: Connect to kafka

<div style='font-size: 25px'>

Connect the tremor instance configured in `./etc/tremor` to the `kafka_feeder` kafka cluster and the topic `tremor` (via onramp) and display received events on stdout.

<hr/>

```sh
./trecker server run -l /pwd/etc/tremor/logger.yaml -f /pwd/etc/tremor/config/config.yaml /pwd/etc/tremor/config/main.trickle
```

`docker kill ...` from another shell to stop.
</div>

---

## Task 1: Solution

```yaml
onramp:
  - id: kafka
    type: kafka
    codec: json
    config:
      brokers:
        - <YOUR_DOCKER_IP>:9092
      topics:
        - tremor
      group_id: lab
```

---

## ✋ Task 2: Cleanup and Classify the Input Data

<div style='font-size: 25px'>

Write a pipeline script that does the following:

* change the field `short_message` to `log_level` and trim and lowercase its contents
* add classifications to the event in field `classifications`:
  - `app_even`: if field `application` starts with the string `app`, immediately followed by an even number. e.g. `app2`
  - `app_odd`: contains field `application` with `app` followed by an odd number.
  - `applog` / `syslog` / `other` - based on whether field `index_type` starts with `applog`, `syslog` or something else.


<hr/>

```sh
./trecker run /pwd/etc/tremor/config/main.trickle -i /pwd/data/input.json
```

</div>

---

## Task 2: Solution

```trickle
define script cleanup
script
  use std::string;
  let event = merge event of 
      { "log_level": string::lowercase(string::trim(event.short_message)), 
        "short_message": null 
      } 
    end;
  end;
end;
create script cleanup;

define script classify
script
  match event of 
    case extracted = %{ "application" ~= re|^app(\d)| }
    default => 
  end;
end;
create script classify;

select event from in into cleanup;
select event from cleanup into classify;
select event from classify into out;
```

---

## ✋ Task 3: Passthrough pipeline v2

<div style='font-size: 25px'>

Introduce a new node called **`process`** in **`apache.trickle`**, based on the <a href="https://docs.tremor.rs/tremor-query/operators/#script">tremor-script operator</a>. The script will also pass in the log line as is, for now.

```
in -> process -> out
```
<hr/>

```sh
# we decode the log lines as plain string (default is to treat them as json)
# the `/pwd/` prefix is needed here to pick up these files from the container
./trecker run /pwd/apache.trickle --decoder string --encoder string -i /pwd/apache_access_logs
```


</div>

---

## Task 3: Solution

```trickle
define script process
script
  event;
end;

create script process;

select event from in into process;
select event from process into out;
# This will additionally print script errors to the
# error port of the pipeline
select event from process/err into err;
```

---

## ✋ Task 4: Parse a log line

<div style='font-size: 25px'>

Using the <a href="https://docs.tremor.rs/tremor-script/extractors/dissect/">dissect extractor</a>, convert the log string into a structured record.

<hr/>

```sh
# get just one log line for testing the parsing logic:
# 127.0.0.1 - - [19/Jun/1998:22:00:05 +0000] "GET /english/images/comp_bg2_hm.gif HTTP/1.0" 200 3785
tail -1 apache_access_logs > test_log_line

# ignore diagnostics from trecker and get the final line only
./trecker run /pwd/apache.trickle --decoder string --encoder string -i /pwd/test_log_line | tail -n1 | jq
```

Output should be:

```json
{
  "ip": "127.0.0.1",
  "timestamp": "19/Jun/1998:22:00:05 +0000",
  "method": "GET",
  "path": "/english/images/comp_bg2_hm.gif",
  "proto": "HTTP/1.0",
  "code": 200,
  "cost": 3785
}
```
</div>

---

## Task 4: Solution

<div style='font-size: 0.75em;'>

```trickle
define script process
script
  match {"log": event} of
    case dissect_result = %{ log ~= dissect|%{ip} %{} %{} [%{timestamp}] "%{method} %{path} %{proto}" %{code:int} %{cost:int}| } =>
      dissect_result.log
    default =>
      emit {"error": "Malformed log line", "event": event} => "err"
  end;
end;

create script process;

select event from in into process;
select event from process into out;

select event from process/err into err;
```

</div>

---

## Task 5: Parse all log lines

<div style='font-size: 25px'>
See if there's any error events when running the above script for all the logs.

```
./trecker run /pwd/apache.trickle --decoder string --encoder string -i /pwd/apache_access_logs
```

For logs with malformed errors, we can try to add a dissect pattern that would match it (leave as an exercise for later).

Also try switching the encoder to something like `yaml`.
</div>

---

## Extra-credit

* Filter out logs with status code < 400 (i.e. only pass error logs)
* Throttle logs such that output is just 10 logs per second
* Each 10 seconds output request duration percentiles by HTTP status code

>>>

## Lab Exercise 2

<div style='font-size: 20px'>

In this section, we'll take the processing from the last
lab and create a deployment from it.

</div>

<div style="font-size: 42px; font-weight: bold;" class="fragment">Time to stay awake!</div>

---

## Goal

Create a deployment for tremor that listens on tcp port `4242` and reads a log per line
then process it via the pipeline we created in the last section.

---


## ✋ Task 1: Create a source

<div style='font-size: 25px'>

Create a **`source.yaml`** with a <a href="https://docs.tremor.rs/artefacts/onramps/#tcp">`tcp` source</a> to listen on `0.0.0.0:4242` for incoming events.

Use a <a href="https://docs.tremor.rs/artefacts/preprocessors/#lines">`lines` preprocessor</a> to split the incoming data by line and a <a href="https://docs.tremor.rs/artefacts/codecs/#string">`string` codec</a>.

</div>

---

## Task 1: Solution

```yaml
# The onramp and offramp sections of configuration specify external sources
# to an instance of tremor server.
#
onramp:
  - id: tcp-input # A unique id for binding/mapping
    type: tcp # The unique type descriptor for the onramp ( websocket server here)
    codec: string # The underlying data format expected for application payload data
    preprocessors: # Split incoming data by line
      - lines
    config:
      port: 4242 # The TCP port to listen on
      host: "0.0.0.0" # The IP address to bind on ( all interfaces in this case )
```

---

## ✋ Task 2: Create a sink

<div style='font-size: 25px'>

Create a **`sink.yaml`** with a <a href="https://docs.tremor.rs/artefacts/offramps/#stdout">stdout sink</a>.

Use the <a href="https://docs.tremor.rs/artefacts/codecs/#json">`json` codec</a> and `>>` as a prefix.

<hr/>

**Reminder**: The offramp sections of configuration specify external sinks to an instance of tremor server.

</div>

---

## Task 2: Solution

```yaml
offramp:
  - id: stdout-output # The unique id for binding/mapping
    type: stdout # The unique type descriptor for the offramp ( stdout here )
    codec: json # The underlying data format expected for application payload data
    config:
      prefix: ">> " # A prefix for data emitted on standard output by this offramp

```

---
## ✋ Task 3: Create a binding

<div style='font-size: 25px'>

Create a **`binding.yaml`**  with a binding `lab02` that links the sink and source to the pipeline.

Note since we called the pipeline file `apache.trickle` the pipeline will be named `apache`.

<hr/>

**Reminder**:
A binding associates sinks and sources with pipeline inputs and outputs
through their unique identifiers to create a deployment graph template. These
typically use variables that are incarnated using runtime mappings so that
bindings can be reused where appropriate.

</div>

---

## Task 3: Solution

```yaml
binding:
  - id: lab02                                    # The unique name of this binding template
    links:
      '/onramp/tcp-input/{instance}/out':        # Connect the source to the pipeline
       - '/pipeline/apache/{instance}/in'
      '/pipeline/apache/{instance}/out':         # Connect the pipeline to the sink
       - '/offramp/stdout-output/{instance}/in'
      '/pipeline/apache/{instance}/err':         # Direct pipeline errors to stdout as well
       - '/offramp/stdout-output/{instance}/in'
```

---

## ✋ Task 4: Create the mapping

<div style='font-size: 25px'>

Create a **`mapping.yaml`** to initialize the binding.

You can use the instance `01` or any other name

<hr/>

**Reminder**: Mappings instanciate bindings and provide the variables / instances for them
to resolve to full names.

</div>

---

## Task 4: Solution

```yaml
mapping:
  /binding/lab02/01:
    instance: "01"
```

---

## Final steps

<div style='font-size: 25px'>

Can be tested with the following commands. Note that once trecker is started you need to
use `docker stop` to stop it again. `CTRL+C` has no effect.

```sh
./trecker server run -f /pwd/apache.trickle /pwd/source.yaml /pwd/sink.yaml /pwd/binding.yaml /pwd/mapping.yaml

# send logs to the tremor tcp receiver
cat apache_access_logs | nc 127.0.0.1 4242
```

</div>

>>>

### You made it through the lab!!!

![yeah](./assets/rickmorty.gif)

>>>
### End of `operations` guide
<!-- .slide: data-background="#33FF77" -->

This is the end of the operations guide

Note: This will only appear in speaker notes window
