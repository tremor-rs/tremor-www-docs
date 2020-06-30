# Benchmarking

This is a short synopsis of benchmarking in tremor

## Scope

How to run individual benchmarks comprising the benchmark suite in tremor.

### Run all benchmarks

```bash
make bench
```

### Run individual benchmarks

In order to run individual benchmarks, issue a command of the form:

```bash
./bench/run <name-of-benchmark>
```

Where:

| variable          | value                                                                               |
| ----------------- | ----------------------------------------------------------------------------------- |
| name-of-benchmark | Should be replaced with the basename of the yaml file for that benchmark's pipeline |

For example:

```bash
./bench/run real-workflow-througput-json
```

Will run the 'real-workflow-througput-json' benchmark and publish a HDR histogram to standard output
upon completion. it takes about 1 minute to run.

## Anatomy of a benchmark

Tremor benchmarks composed of:

- An impossibly fast source of data - using the blaster onramp
- An impossibly fast sink of data - using the blackhole offramp
- A pipeline that is representative of the workload under measurement

### Example blaster onramp configuration

Blaster loads data from a compressed archive and reads json source data line by line into memory. The in memory cached copy is replayed repeatedly forever.

```yaml
---
onramp:
  - id: blaster
    type: blaster
    codec: json
    config:
      source: ./demo/data/data.json.xz
```

### Example blackhole offramp configuration

Blackhole is a null sink for received data. It also records the latency from ingest time ( created and enqueued in blaster ) to egress ( when it hits the blackhole ) of an event.

As such, blaster and blackhole are biased 'unreasonably fast' and they capture intrinsic performance - or, the best case performance that tremor can sustain for the representative workload.

Blackhole uses high dynamic range histograms to record performance data ( latency measurements ).

```yaml
offramp:
  - id: blackhole
    type: blackhole
    codec: json
    config:
      warmup_secs: 10
      stop_after_secs: 100
      significant_figures: 2
```

The pipeline and binding configuration will vary by benchmark, for the real world throughput benchmark they are structured as follows:

```yaml
pipeline:
  - id: main
    interface:
      inputs:
        - in
      outputs:
        - out
    nodes:
      - id: runtime
        op: runtime::tremor
        config:
          script: |
            match event.application of
              case "app1" => let $class = "applog_app1",  let $rate = 1250, let $dimension = event.application, emit event
              case "app2" => let $class = "applog_app1",  let $rate = 2500, let $dimension = event.application, emit event
              case "app3" => let $class = "applog_app1",  let $rate = 18750, let $dimension = event.application, emit event
              case "app4" => let $class = "applog_app1",  let $rate = 750, let $dimension = event.application, emit event
              case "app5" => let $class = "applog_app1",  let $rate = 18750, let $dimension = event.application, emit event
              default => null
            end;
            match event.index_type of
              case "applog_app6" => let $class = "applog_app6", let $rate = 4500, let $dimensions = event.logger_name, emit event
              case "syslog_app1" => let $class = "syslog_app1", let $rate = 2500, let $dimensions = event.syslog_hostname, emit event
              default => null
            end;
            match array::contains(event.tags, "tag1") of
              case true => let $class = "syslog_app2", let $rate = 125, let $dimensions = event.syslog_hostname, emit event
              default => null
            end;
            match event.index_type of
              case "syslog_app3" => let $class = "syslog_app3", let $rate = 1750, let $dimensions = event.syslog_hostname
              case "syslog_app4" => let $class = "syslog_app4", let $rate = 7500, let $dimensions = event.syslog_hostname
              case "syslog_app5" => let $class = "syslog_app5", let $rate = 125, let $dimensions = event.syslog_hostname
              case "syslog_app6" => let $class = "syslog_app6", let $rate = 3750, let $dimensions = event.syslog_hostname
              default => let $class = "default", let $rate = 250
            end;
            event;
      - id: group
        op: grouper::bucket
    links:
      in: [runtime]
      runtime: [group]
      group: [out]
      group/overflow: [out]
```

## Other

All the above configuration are provided in a single yaml file and evaluated through the `run` script. The make target `bench` calls the run script for each known benchmark file and redirects test / benchmark output into a file.

## Recommendations

To account for run-on-run variance ( difference in measured or recorded performance from one run to another ) we typically run benchmarks repeatedly on development machines with non-essential services such as docker or other services not engaged in the benchmark such as IDEs shut down during benchmarking.

Even then, development laptops are not lab quality environments so results should be taken as indicative and with a grain of salt.
