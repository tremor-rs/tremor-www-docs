# CNCF OpenTelemetry Passthrough

This example is the simplest possible configuration of tremor with support for CNCF OpenTelemetry
interception and distribution. It shows the very basic building blocks:
* CNCF OpenTelemetry Onramp
* CNCF OpenTelemetry Offramp
* Deployment configuration file

External open telemetry clients can use port `4316` to send OpenTelemetry logs, traces and metrics
through tremor. Tremor prints the json mapping to standard out and forwards the events to the
OpenTelemetry collector.

## Environment

The [onramp](etc/tremor/config/00_ramps.yaml) we use is the `otel` CNCF OpenTeletry onramp listening on
a non-standard CNCF OpenTelemetry port `4316`, it receives protocol buffer messages over gRPC on this
port. The log, metric and trace events received are converted to tremor's value system and passed through
a passthrough pipeline to the CNCF OpenTelemetry sink. The sink will try to connect to a downstream CNCF
OpenTelemetry endpoint. In this workshop we will use the well known OpenTelemetry port of `4317` for our
sink and run the standard OpenTelemetry collector on this port using its a simple [collector configuration](etc/otel/collector-config.yaml).

```yaml
onramp:
  - id: otlp
    type: otel # Use the OpenTelemetry gRPC listener source
    codec: json # Json is the only supported value
    config:
      port: 4316 # The TCP port to listen on
      host: "0.0.0.0" # The IP address to bind on ( all interfaces in this case )
```

It connects to a simple passthrough pipeline. This pipeline forwards any received
observability events downstream unchanged.

```trickle
select event from in into out;
```

We connect the passthrough output events into an OpenTelemetry sink which distributes them to
a downstream OpenTelemetry service.

```yaml
offramp:
  - id: otlp
    type: otel
    codec: json # Jsn is the only supported value
    config:
      host: "0.0.0.0"
      port: 4317
```

The [binding](./etc/tremor/config/01_binding.yaml) expresses these relations and gives deployment connectivity graph.

```yaml
binding:
  - id: example
    links:
      '/onramp/otlp/{instance}/out':
       - '/pipeline/example/{instance}/in'
      '/pipeline/example/{instance}/out':
       - '/offramp/stdout/{instance}/in'
       - '/offramp/otlp/{instance}/in'
```

Finally the [mapping](./etc/tremor/config/02_mapping.yaml) instanciates the binding with the given name and instance variable to activate the elements of the binding.

```yaml
mapping:
  /binding/example/passthrough:
    instance: "passthrough"
```

## Business Logic

```trickle
select event from in into out
```

## Command line testing during logic development

Use any compliant OpenTelemetry instrumented application and configure the
server to our source on port `4316` instead of the default `4317`.

## Docker

For convenience, use the provided [docker-compose.yaml](./docker-compose.yaml) to
start and stop tremor and the opentelemetry collector as follows:

```bash
# Start
$ docker-compose up

# Stop
$ docker-compose stop
```
