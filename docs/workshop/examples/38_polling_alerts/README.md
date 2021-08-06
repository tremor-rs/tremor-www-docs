# Polling

!!! note
    All the application code here is available from the docs [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/38_polling_alerts).

This example demonstrates using Tremor to periodically poll a data source (we use influx as it can quickly generate data) and make decisions based on the results - in our case alert us on low CPU or memory.

We will not dive deep into the query used or the alerts defined as they're only supporting elements to the story we're trying to tell here: periodic, reactive workflows. To this end, we leverage a good bit of the configuration introduced in [the influx example](../11_influx/README.md).

## Environment


As mentioned above, we reuse a lot of the influx logic, so we ignore the following artifacts:

- onramp: `udp-input`
- offramp: `influx-output`
- query: `ingress`
- binding: `ingress`
- mapping: `ingress`

Also there are two new pipelines:

- `poll` - translates a tick into a query
- `alert` - translates the result and evaluates if an alert should be triggered

We also have a new onramp (`tick`) and offramp (`influx-query`).

For the sake of not repeating the previous workshop we will focus on those new parts exclusively.

## Business Logic

### Polling

This section deals with polling, in our case we want to query influxdb on a periodic interval.

To this end we use a `metronome` onramp that fires an event every 10s. We send the events into [`poll.trickle`](./etc/tremor/config/poll.trickle) where we create a influx request out of the metronom event.

The `poll` pipeline then connects to the linked influx offramp to run the query.

```trickle
# poll.trickle
# This file is for for turning ticks into queries

# this turns the `metronom` tick into a query
define script query
with
  host = "",
  db = ""
script
  use std::url;
  # we define the query to gather data
  # this is the original, for the sake of dockerizing it we ignore the host in the final query since we don't know what it will be
  # let query = "SELECT mean(\"usage_idle\") AS \"cpu_idle\", mean(\"active\") AS \"mem_active\" FROM \"tremor\".\"autogen\".\"cpu\", \"tremor\".\"autogen\".\"mem\" WHERE time > now() - 1h AND time < now() AND \"host\"='#{ args.host }' GROUP BY time(1h) FILL(null)";
  let query = "SELECT mean(\"usage_idle\") AS \"cpu_idle\", mean(\"active\") AS \"mem_active\" FROM \"tremor\".\"autogen\".\"cpu\", \"tremor\".\"autogen\".\"mem\" WHERE time > now() - 1h AND time < now() GROUP BY time(1h) FILL(null)";
  # we encode this to a rest offramp query parameter using `url::encode`
  let $endpoint.query = "db=#{ args.db }&epock=ms&q=#{ url::encode(query) }";
  let event.meta = $;
  # we can end this script
  event
end;

# we create a script for a given host
create script query with
  host = "d111f17774f7"
end;
# we wire it all up
select event from in into query;
select event from query into out;
```

### Alerting

The [`alert.trickle`](./etc/tremor/config/alert.trickle) pipeline takes the reply from Influx and alert if the values we see are above a given limit.

Since the influx reply uses a unique datamodle, we need to unscramble the results, this sadly is a trail and error process based on what influx returns.

Once we have extracted the data we can pass it into an alerting script that checks a few conditions in a given order. The first condition that is met will trigger the coresponding alert.


You can adopt the alert conditions in the `with` section of the script.

```trickle
# This script takes the responses and turns them into alerts

# The script that does all the logic, we define our alerts here
define script alert with
  cpu_limit = 100,
  mem_limit = 19518531180
script
  match event of
    case %{cpu_idle < args.cpu_limit, mem_active > args.mem_limit} => emit "EVERYTHING IS ON FIRE"
    case %{cpu_idle < args.cpu_limit} => match event of
      case %{cpu_system > 50} => emit "OS BROKEN"
      default => emit "CPU BUSY"
    end

    case %{mem_active > args.mem_limit } => emit "MEM LOW"
    default => drop
  end
end;

create script alert;

# Since the influx reply is hard to work with we santize it here so we can write our alerts
# in a cleaner fashipn
#
# example result:
# ```
# {"results":[{"statement_id":0,"series":[{"columns":["time","cpu_idle1","mem_active"],"values":[["2021-03-02T15:00:00Z",98.856058199546,null],["2021-03-02T16:00:00Z",97.09260215835516,null]],"name":"cpu"},{"columns":["time","cpu_idle1","mem_active"],"values":[["2021-03-02T15:00:00Z",null,19519109501.023254],["2021-03-02T16:00:00Z",null,19959332287.756653]],"name":"mem"}]}]}
# ```
create stream extracted;
select {
  "#{event.results[0].series[0].columns[1]}": event.results[0].series[0].values[1][1],
  "#{event.results[0].series[1].columns[2]}": event.results[0].series[1].values[1][2],
} from in into extracted;

# we wire it all up
select event from extracted into alert;
select event from alert into out;

# we could use this for debugging
# select event from in into out;
```

## Command line testing during logic development

```bash
$ docker compose up
  ... lots of logs ...
```

Then watch alerts on stdout from `docker compose`.
