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


<div style='font-size: 0.75em;'>

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
	use std::integer;
	use std::array;

	match event of
		case %{} =>
			let event["classifications"] = []
		default => 1
	end;
	match event of
		case app = %{ application ~= re|^app(?P<num>\\d)| } =>
			let category = match integer::parse(app.application.num) % 2 of
				case 0 => "app_even"
				default => "app_odd"
			end,
			let event["classifications"] = array::push(event["classifications"], category)
		default => -1
	end;
  let cls = match event of
		case %{ index_type ~= glob|applog*| } => "applog"
		case %{ index_type ~= glob|syslog*| } => "syslog"
    default => "other
  end;
	let event["classifications"] = array::push(event["classifications"], cls);
  event
end;
create script classify;

select event from in into cleanup;
select event from cleanup into classify;
select event from classify into out;
```

</div>

---

## ✋ Task 3: Rate-Limiting

<div style='font-size: 25px'>

Rate-Limit all events down to a maximum rate of 1 event per second, using the [`grouper::bucket`](https://docs.tremor.rs/tremor-query/operators/#grouperbucket) operator.

<hr/>

```sh
# validate - events should appear at much slower rate
./trecker server run ...
```

</div>

---

## Task 3: Solution

<div style='font-size: 0.75em;'>

```trickle
define grouper::bucket operator rate_limit;
create operator rate_limit;

define script rate_limit_prepare
script
  let $class = "rate-limited";
  let $rate = 1; # 1 event per second
  event
end;
create script_rate_limit_prepare;

select event from in into cleanup;
select event from cleanup into classify;
select event from classify into rate_limit_prepare;
select event from rate_limit_prepare into rate_limit;
select event from rate_limit into out;

```

</div>

---

## ✋ Task 3a: Advanced Rate Limiting

<div style='font-size: 25px'>

Rate-limit events differently by their classification:

* `applog`: each different `application` is rate-limited to 1 event per second
* `syslog`: apply rate-limit of 1 event per second for each `syslog_hostname`

<hr/>

</div>

---

## Task 3a: Solution

<div style='font-size: 0.75em;'>

```trickle
ANUP: TODO
```

</div>

---

## ✋ Task 4: Linked Transport - Elastic

<div style='font-size: 25px'>
Send rate-limited events to Elastic via [elastic offramp](https://docs.tremor.rs/artefacts/offramps/#elastic) and investigate response events on stdout/stderr.

```
docker-compose -f elastic-compose.yaml up
```

```
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>
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
        - http://<DOCKER_IP>:9200
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


