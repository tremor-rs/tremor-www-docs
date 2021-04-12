# Operators

Operators are part of the pipeline configuration.

Operators process events and signals in the context of a pipeline. An operator, upon receiving an event from an upstream operator or stream, MAY produce one or many events to one or many downstream directly connected operators. An operator MAY drop events which halts any further processing.

Operators allow the data processing capabilities of tremor to be extended or specialized without changes to runtime behavior, concurrency, event ordering or other aspects of a running tremor system.

Operators are created in the context of a pipeline and configured as part of `tremor-query` [statements](index.md#custom-operator-definitions). An operator MUST have an identifier that is unique for its owning pipeline.

Configuration is of the general form:

```trickle
define module::operator_name operator my_custom_operator
with
  param1 = "foo",
  param2 = [1, 2, 3]
end;

# create - full form
create operator my_custom_operator_instance from my_custom_operator
with
  param1 = "bar",
  param2 = [true, false, {}]
end;

# create - short form
create operator my_custom_operator;
```

## script

An embedded tremor script is created with a special syntax that deviates from the operator creation. For a full reference see the section on [tremor-query embedded-scripts](index.md#embedded-script-definitions).

The tremor script runtime allows to modify events or their metadata. To learn more about Tremor Script please see the [related section](../tremor-script/index.md).

**Outputs**:

- `out` (default output used with `emit`)
- `error` - channel for runtime errors
- `<anything else>` used when `emit event => "<anything else>"`

**Examples**:

```trickle
# definition
define script rt
script
  emit
end;
```

```trickle
define script add
script
  emit + 1
end;

create script add;

select event from in into add;
select event from add into out;
```



## grouper::bucket

Bucket will perform a sliding window rate limiting based on event metadata. Limits are applied for every `$class`. In a `$class` each `$dimensions` is allowed to pass `$rate` messages per second.

This operator does not support configuration.

**Metadata Variables**:

- `$class` - The class of an event. (String)
- `$rate` - Allowed events per second per class/dimension (Number)
- (Optional) `$dimensions` - The dimensions of the event. (Any)
- (Optional)`$cardinality` - the maximum number of dimensions kept track of at the same time (Number, default: `1000`)

**Outputs**:

- `out`
- `error` - Unprocessable events for example if `$class` or `$rate` are not set.
- `overflow` - Events that exceed the rate defined for them

**Example**:

```trickle
define grouper::bucket operator group;
```

**Metrics**:

The bucket operator generates additional metrics. For each class the following two statistics are generated (as an example):

```json
{"measurement":"bucketing",
 "tags":{
   "action":"pass",
   "class":"test",
   "direction":"output",
   "node":"bucketing",
   "pipeline":"main",
   "port":"out"
 },
 "fields":{"count":93},
 "timestamp":1553012903452340000
}
{"measurement":"bucketing",
 "tags":{
   "action":"overflow",
   "class":"test",
   "direction":"output",
   "node":"bucketing",
   "pipeline":"main",
   "port":"out"
 },
 "fields":{"count":127},
 "timestamp":1553012903452340000
}
```

This tells us the following, up until this measurement was published in the class `test`:

- (`pass`) Passed 93 events
- (`overflow`) Marked 127 events as overflow due to not fitting in the limit

## generic::backpressure

This operator is deprecated please use `qos::backpressure` instead.

## qos::backpressure

The backpressure operator is used to introduce delays based on downstream systems load. Longer backpressure steps are introduced every time the latency of a downstream system reached `timeout`, or an error occurs. On a successful transmission within the timeout limit, the delay is reset.

**Configuration options**:

- `timeout` - Maximum allowed 'write' time in milliseconds.
- `steps` - Array of values to delay when a we detect backpressure. (default: `[50, 100, 250, 500, 1000, 5000, 10000]`)

**Outputs**:

- `out`
- `overflow` - Events that are not let past due to active backpressure

**Example**:

```trickle
define qos::backpressure operator bp
with
  timeout = 100
end;
```

## qos::percentile

An alternative traffic shaping option to backpressure. Instead of all dropping events for a given
time we drop a statistical subset with an increasing percentage of events dropped the longer we
see errors / timeouts.

In general `step_up` should always be significantly smaller then `step_down` to ensure we gradually
reapproach the ideal state.

**Configuration options**:

- `timeout` - Maximum allowed 'write' time in milliseconds.
- `step_down` - What additional percentile should be dropped in the case of a timeout (default 5%: `0.05`)
- `step_up` - What percentile should be recovered in case of a good event. (default: 0.1%: `0.001`)

**Outputs**:

- `out`
- `overflow` - Events that are not let past due to active backpressure

**Example**:

```trickle
define qos::percentile operator as perc
with
  timeout = 100,
  step_down = 0.1 # 10%
end;
```

## qos::roundrobin

Evenly distributes events over it's outputs. If a CB trigger event is received from an output this
output is skipped until the circuit breaker is restored. If all outputs are triggered the operator
itself triggers a CB event.

**Outputs**:

- `*` (any named output is possible)

**Example**:

```trickle
define qos::roundrobin operator roundrobin
with
  outputs = ["round", "robin", "outputs"]
end;
```

## qos::wal

A Write Ahead Log that will persist data to disk and feed the following operators from this disk
cache. It allows to run onramps that do not provide any support for delivery guarantees with
offramps that do.

The wal operator will intercept and generate it's own circuit breaker events. You can think about it
as a firewall that will protect all operators before itself from issues beyond it. On the other hand
it will indiscriminately consume data from sources and operators before itself until it's own
circuit breaking conditions are met.

At the same time will it interact with tremors guaranteed delivery system, events are only removed
from disk once they're acknowledged. In case of delivery failure the WAL operator will replay the
failed events. On the same way the WAL operator will acknowledge events that it persists to disk.

The WAL operator should be used with caution, since every event that passes through it will be
written to the hard drive it has a significant performance impact.

**Configuration options**:

- `read_count` - Maximum number of events that are read form the WAL at one time.
- `dir` - Directory to store the WAL-file in (optional, if omitted the WAL will remain in memory and not be
  persisted to disk)
- `max_elements` - Maximum number of elements the WAL will cache before triggering a CB event
- `max_bytes` - Maximum space on disk the WAL should take (this is a soft limit!)

Only one of `max_elements` or `max_bytes` is required, setting both is possible.

**Outputs**:

- `out`

**Example**:

```trickle
define qos::wal operator wal with
  dir = "./wal",
  read_count = 20,
  max_elements = 1000,
  max_bytes = 10485760
end;
```

## generic::batch

The batch operator is used to batch multiple events and send them in a bulk fashion. It also allows to set a timeout of how long the operator should wait for a batch to be filled.

Supported configuration options are:

- `count` - Elements per batch
- `timeout` - Maximum delay between the first element of a batch and the last element of a batch.

**Outputs**:

- `out`

**Example**:

```trickle
define generic::batch operator batch with
  count = 300
end;
```

## generic::counter

Keeps track of the number of events as they come and emits the current count out alongside the event. The output is a record of the form `{"count": n, "event": event}`, where `n` is the current count and `event` is the original event.

The counter starts when the first event comes through and begins from 1.

**Outputs**:

- `out`

**Example**:

```trickle
define generic::counter operator counter;
```

## debug::history

!!! note

    This operator is for debugging purposes only, and should not be used in production deployments.

This operator generates a history entry in the event metadata underneath the field provided in the `name` config value. Data is pushed to the array as a Striong in the form: `"event: <op>(<event_id>)"`.

This can be used as a tracepoint of events in a complex pipeline setup.

**Configuration options**:

- `op` - The operation name of this operator
- `name` - The field to store the history on

**Outputs**:

- `out`

**Example**:

```trickle
define debug::history operator history with
  op = "my-checkpoint",
  name = "event_history"
end;
```
