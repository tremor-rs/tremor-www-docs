# Configuration Walkthrough

A short canned synopsis of configuration tremor.

This guide walks through configuring tremor via its API directly and via its command line tool 'tremor'. For the API, we use 'curl' on the command line.

## Introduction

In this walkthrough we will deploy a tremor pipeline that generates a periodic sequence of messages or heartbeats every second. The solution is composed of the following tremor artefacts:

- A metronome onramp - our periodic message generator
- A stdout offramp - an offramp that serializes to standard output useful for debugging
- A pipeline - we pass the input ( metronome events ) to our output

In this walkthrough we configure a single onramp, offramp and pipeline but many other configurations are possible.

## Prerequisites

### Write an onramp specification

This creates a config specification for an onramp that can be referenced by the unique id `metronome`. It does not create an instance of it.

```yaml
# File: metronome-onramp.yaml
id: metronome
type: metronome
config:
  interval: 1000
```
### Write an offramp specification

This creates a config specification for an offramp that can be referenced by the unique id `stdout`. It does not create an instance of it. Think of this as a blueprint.

```yaml
# File: metronome-offramp.yaml
id: stdout
type: stdout
```

### Write a pipeline specification

File: `main.trickle`:

```tremor
#!config id = "main"
select event from in into out;
```

### Write a binding specification

In tremor pipelines have no non-deterministic side-effects.

By design, tremor does not allow onramps or offramps to be specified as a part of a pipeline. This would couple running pipelines to external connections. For example, to an external kafka broker and topic. This isn't bad per se, but it would allow a configuration or programming style that allows pipelines that are hard to distribute, clusterable or scalable.

To be clear, therefore:

- All data processed by a tremor pipeline is always ingested via an event
- All events arrive into pipelines via 'input streams', operators that link a pipeline to the outside world
- All events leave a pipeline via 'output streams', operators that link a pipeline to the outside world
- Events always traverse a pipeline in graph order ( Depth-First-Search )
- Where there is no imposed ordering ( in a branch ), tremor imposes declaration order
- Synthetic events ( signals from the tremor system runtime, or contraflow that derive from events already in-flight in a pipeline ) follow the same rules, without exception.
- All in-flight events in a pipeline are processed to completion before queued events are processed.

As a result, in order to connect onramps, offramps and pipelines , we need to link them together. We call this set of ( required ) links a 'binding specification'. It is ok _not_ to connect a pipeline input stream or output stream. But it is not ok to not connect the subset exposed in a binding specification.

For our scenario, the following will suffice:

```yaml
# File: metronome-binding.yaml
id: default
links:
  "/onramp/metronome/{instance}/out": ["/pipeline/main/{instance}/in"]
  "/pipeline/main/{instance}/out": ["/offramp/stdout/{instance}/in"]
```

Ths creates a binding specification. Again this does not instantiate the referenced onramps, offramps or pipelines. This is also just a blueprint of a connected topology with a unique identifier `default`.

## Publish via the REST API / curl

### Publish onramp specification

```bash
curl -vs -stderr -X POST -H "Content-Type: application/yaml" --data-binary @metronome-onramp.yaml http://localhost:9898/onramp
```

Check that it published ok:

```bash
$ curl -vs --stderr - -H "Accept: application/yaml" http://localhost:9898/onramp
- metronome
```

### Publish offramp specification

```bash
curl -vs -stderr -X POST -H "Content-Type: application/yaml" --data-binary @metronome-offramp.yaml http://localhost:9898/offramp
```

Check that it published ok:

```bash
curl -vs --stderr - -H "Accept: application/yaml" http://localhost:9898/offramp
- stdout
```

### Publish pipeline specification

```bash
curl -vs --stderr -X POST -H "Content-type: application/vnd.trickle" --data-binary @main.trickle http://localhost:9898/pipeline
```

Check that it published ok:

```bash
$ curl -vs --stderr -H "Accept: application/vnd.trickle" http://localhost:9898/pipeline/main
#!config id = "main"
select event from in into out;
```

### Publish binding specification

```bash
curl -vs -stderr -X POST -H "Content-Type: application/yaml" --data-binary @metronome-binding.yaml http://localhost:9898/binding
```

```bash
$ curl -vs --stderr - -H "Accept: application/yaml" http://localhost:9898/binding
- default
```

### Publish metronome offramp specification

```bash
curl -vs -stderr -X POST -H "Content-Type: application/yaml" --data-binary @metronome-offramp.yaml http://localhost:9898/offramp
```

Check that it published ok:

```bash
curl -vs --stderr - -H "Accept: application/yaml" http://localhost:9898/offramp
- default
```

## Publish via tremor

The tremor command allows the exact sample set of interactions as above. For brevity we simpilify the examples in this section but the steps are the same.

Tremor tool, however, makes it easier to switch between JSON and YAML

### Publish all specifications

Publish onramp, offramp, pipeline and binding:

```bash
tremor api onramp create metronome-onramp.yaml
tremor api offramp create metronome-offramp.yaml
tremor api pipeline create metronome-pipeline.yaml
tremor api binding create metronome-binding.yaml
```

Check all our artefacts have published ok:

```bash
tremor api onramp list
tremor api offramp list
tremor api pipeline list
tremor api binding list
```

## Limitations

Live deployments via the API only work with a single entity and passing a list using the API isn't supported. In order to achieve that you can use ['Static or Bootstrap Deployments](./configuration.md)

## Deployment

Once all artefacts are published into the tremor repository we are ready to deploy. We deploy instances, via bindings, through mapping specifications.

In all steps to this point, we have been populating the tremor repository. Like a git repository the tremor repository stores artefacts, like git stores code.

When we publish a mapping we are deploying live instances of onramps, offramps, and pipelines, in our case, we want to:

- Deploy a single metronome onramp instance
- Deploy a single stdout offramp instance
- Deploy a single passthrough pipeline
- We want the onramp to connect to the pipeline
- We want the offramp to connect to the pipeline

In our final step we specify:

- We want to call our instance 'walkthrough'

A Mapping specification contains values for the placeholders (with curly braces, e.g. `{instance}`) in the binding specification.
```yaml
# File: metronome-mapping.yaml
instance: "walkthrough"
```

We do not deploy or publish a mapping, we rather instantiate a binding specification and provide a mapping with the placeholder values.

Deploy via curl:

```bash
curl -vs -stderr -X POST -H "Content-Type: application/yaml" --data-binary @metronome-mapping.yaml http://localhost:9898/binding/default/walkthrough
```

Deploy via tremor:

```bash
tremor api binding activate default walkthrough metronome-mapping.yaml
```

The result is that all referenced onramps, offramps and pipelines specified in the binding are live and linked and events flow through them.