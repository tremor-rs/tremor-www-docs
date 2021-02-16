<!-- .slide: data-background="#333333" -->

## Tremor Intermediate Workshop - 1

- Connecting to Kafka
- Tremor-query (Trickle) and Tremor-script
- Rate-Limiting
- Group By and Windows
- Linked Transport

---

## Lab Exercise 1

<div style='font-size: 20px'>

In this section, we will gradually build a solution for processing structured log messages
from Kafka, transforming, classifying and rate-limiting them.
</div>

---

## Requirements

- Docker
- docker-compose

---

## Task 0: Set up lab materials

```sh
git clone git@github.com:tremor-rs/tremor-www-docs.git
cd tremor-www-docs/course/intermediate-lab

# copy the trecker script to intermediate-lab directory for easier access
# optional: can place the script somewhere in your $PATH
cp ../scripts/trecker .

# validate. should give cli usage
./trecker -h
```

---

## ✋ Task 1: Connect to kafka

__Preparation__

Start kafka and kafka_feeder (this will occupy your shell):

```sh
make start-kafka
```

<div style='font-size: 20px'>
This feeds the sample data continuously to a topic named `tremor` in the kafka cluster.
</div>

---

## ✋ Task 1: Connect to kafka

<div style='font-size: 25px'>

Configure the tremor instance in `./etc/tremor` to read from topic `tremor` in the `kafka_feeder` kafka cluster, displaying received events on stdout.

<hr/>

```sh
make start-tremor # watch the shell where you started the compose
```

`make stop-tremor` to stop.
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
        - kafka:9092
      topics:
        - tremor
      group_id: lab
```

---

## ✋ Task 2a: Cleanup Input Data

<div style='font-size: 25px'>

Write a pipeline script that renames the field `short_message` to `log_level`, trimming and lowercasing its contents.

Before:

```json
  ...
  "short_message": "ERROR",
  "logger_name": "logger3",
  ...
```

After:

```json
  ...
  "log_level": "error",
  "logger_name": "logger3",
  ...
```

<hr/>

Iterate on the logic with:

```sh
./trecker run /pwd/etc/tremor/config/main.trickle -i /pwd/data/input.json
```

</div>

---

## Task 2a: Solution


<div style='font-size: 0.75em;'>

```trickle
define script cleanup
script
  use std::string;

  let event = merge event of
    {
      "log_level": string::lowercase(string::trim(event.short_message)),
      "short_message": null
    }
  end;

  # alt method: using patch only
  #let event = patch event of
  #  upsert "log_level" => string::lowercase(string::trim(event.short_message)),
  #  erase "short_message"
  #end;

  # alt method: path-based assignment and patch
  #let event.log_level = string::lowercase(string::trim(event.short_message));
  #let event = patch event of
  #  erase "short_message"
  #end;
end;

create script cleanup;

select event from in into cleanup;
select event from cleanup into out;

select event from cleanup/err into err;
```

</div>

---

## ✋ Task 2b: Classify the Input Data

<div style='font-size: 25px'>

Add a new field `class` to the event, with value based on the contents of the `index_type` field.
  - `applog`: if field `index_type` starts with the string `applog`
  - `syslog`: if field `index_type` starts with the string `syslog`
  - `other`: all other events

<hr/>

```sh
./trecker run /pwd/etc/tremor/config/main.trickle -i /pwd/data/input.json
```

</div>

---

## Task 2b: Solution


<div style='font-size: 0.75em;'>

```trickle
# defintion for cleanup script redacted for length (see task 2a)

define script classify
script
  let event.class = match event of
    case %{ index_type ~= glob|applog*| } => "applog"
    case %{ index_type ~= glob|syslog*| } => "syslog"
    default => "other"
  end;

  event
end;

create script cleanup;
create script classify;

select event from in into cleanup;
select event from cleanup into classify;
select event from classify into out;

select event from cleanup/err into err;
select event from classify/err into err;
```

</div>

---

## ✋ Task 2c: Tag the Input Data

<div style='font-size: 25px'>

Add a new value to the `tags` array in the event, indicating the application's oddness or evenness.
  - `app_even`: if field `application` starts with the string `app`, immediately followed by an even number. e.g. `app2`
  - `app_odd`: if field `application` starts with the string `app`, immediately followed by an odd number. e.g. `app3`

<hr/>

```sh
./trecker run /pwd/etc/tremor/config/main.trickle -i /pwd/data/input.json
```

</div>

---

## Task 2c: Solution


<div style='font-size: 0.75em;'>

```trickle
# defintion for cleanup and classify scripts redacted for length (see task 2a, 2b)

define script tag
script
  use std::integer;
  use std::array;

  match event of
    case app = %{ application ~= re|^app(?P<num>\\d)| } =>
      let tag = match integer::parse(app.application.num) % 2 of
        case 0 => "app_even"
        default => "app_odd"
      end,
      let event.tags = array::push(event.tags, tag)
    default => null
  end;

  event
end;

create script cleanup;
create script classify;
create script tag;

select event from in into cleanup;
select event from cleanup into classify;
select event from classify into tag;
select event from tag into out;

select event from cleanup/err into err;
select event from classify/err into err;
select event from tag/err into err;
```

</div>

---


## ✋ Task 3a: Basic Rate Limiting

<div style='font-size: 25px'>

Rate-Limit all events down to a maximum rate of 1 event per second, using the [`grouper::bucket`](https://docs.tremor.rs/tremor-query/operators/#grouperbucket) operator.

<hr/>

```sh
# validate - events should appear at much slower rate
make restart-tremor
```

</div>

<div style='font-size: 15px'>
Tip: You may modify the `classify` script to assign the `$class` and `$rate` meta variables that the bucket operator uses.
</div>

---

## Task 3a: Solution

<div style='font-size: 0.75em;'>

```trickle
# defintion for cleanup and tag scripts redacted for length (see task 2a, 2b)

define script classify
script
  let event.class = match event of
    case %{ index_type ~= glob|applog*| } => "applog"
    case %{ index_type ~= glob|syslog*| } => "syslog"
    default => "other"
  end;

  let $class = "default";
  let $rate = 1; # 1 event per second

  event
end;

define grouper::bucket operator rate_limit;

create script cleanup;
create script classify;
create script tag;
create operator rate_limit;

select event from in into cleanup;
select event from cleanup into classify;
select event from classify into tag;
select event from tag into rate_limit;
select event from rate_limit into out;

select event from cleanup/err into err;
select event from classify/err into err;
select event from tag/err into err;
```

</div>

---

## ✋ Task 3a: Advanced Rate Limiting

<div style='font-size: 25px'>

Rate-limit events differently based on the value of `event.class` field (which was computed earlier):

* `applog`: 2 event per second for each application (via `application` field)
* `syslog`: 3 event per second for each host (via `syslog_hostname` field)
* `other`:  4 event per second for all other events

<hr/>

```sh
# validate - events should appear at much faster rate (compared to that in 3a)
make restart-tremor
```

</div>

<div style='font-size: 15px'>
Tip: You may modify the `classify` script to conditionally assign the `$rate` variable that the bucket operator uses.
</div>

---

## Task 3a: Solution

<div style='font-size: 0.75em;'>

```trickle
# definition for cleanup and tag scripts redacted for length (see task 2a, 2b)

define script classify
script
  let event.class = match event of
    case %{ index_type ~= glob|applog*| } => "applog"
    case %{ index_type ~= glob|syslog*| } => "syslog"
    default => "other"
  end;

  let $class = event.class;

  # we can also merge this logic with match block above
  match event.class of
    case "applog" =>
      # assumption is that application field is always present for applogs
      let $dimensions = event.application,
      let $rate = 2
    case "syslog" =>
      # assumption is that syslog_hostname field is always present for syslogs
      let $dimensions = event.syslog_hostname,
      let $rate = 3
    case "other" =>
      let $rate = 4
    default =>
      null
  end;

  event
end;

define grouper::bucket operator rate_limit;

create script cleanup;
create script classify;
create script tag;
create operator rate_limit;

select event from in into cleanup;
select event from cleanup into classify;
select event from classify into tag;
select event from tag into rate_limit;
select event from rate_limit into out;

select event from cleanup/err into err;
select event from classify/err into err;
select event from tag/err into err;
```

</div>

---

## ✋ Task 4: Linked Transport - Elastic

<div style='font-size: 25px'>

Send rate-limited events to Elastic via [elastic offramp](https://docs.tremor.rs/artefacts/offramps/#elastic) and investigate response events on stdout/stderr.

```sh
make start-elastic
```

</div>

---

## Task 4: Solution

```yaml
offramp:
  - id: elastic
    type: elastic
    linked: true
    config:
      nodes:
        - http://elastic:9200
  - id: es_stderr
    type: stderr
    config:
      prefix: "[ERR] "
  - id: es_stdout
    type: stdout
    config:
      prefix: "[OUT] "


binding:
  - id: intermediate_lab
  - links:
      "/onramp/placeholder/{instance}/out":
        - "/pipeline/main/{instance}/in"
      "/pipeline/main/{instance}/out":
        - "/offramp/elastic/{instance}/in"

      "/offramp/elastic/{instance}/out":
        - "/pipeline/system::passthrough/{instance}_out/in"
      "/pipeline/system::passthrough/{instance}_out/out":
        - "/offramp/es_stdout/{instance}/in"

      "/offramp/elastic/{instance}/err":
        - "/pipeline/system::passthrough/{instance}_err/in"
      "/pipeline/system::passthrough/{instance}_err/out":
        - "/offramp/es_stderr/{instance}/in"

```

---

>>>

### You made it through the lab!!!

![yeah](./assets/rickmorty.gif)


