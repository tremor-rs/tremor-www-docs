# Linked Transports

!!! attention
    Linked transports are in alpha status as of v0.9.0 and we recommend its use only for exploratory projects. Details around it (including any on this page) are likely to change, as the feature set matures.

Tremor supports ingestion of events from external sources ([onramps](../artefacts/onramps.md)) and after processing them from pipelines, they can be written to external sinks ([offramps](../artefacts/offramps.md)). Since v0.9, Tremor also supports Linked Transports (LT): a mechanism that allows linking of source and sink nature into one ramp artefact.

In other words -- once this mechanism is turned on -- a Tremor onramp can behave as an *offramp* (i.e. send events to the outside world) and similarly, a Tremor offramp can behave as an *onramp* (i.e. receive events from the outside world). This is specifically useful for onramps and offramps like REST and websocket, where the protocol already provides facility for responding to events, and as such, the mechanism is currently supported for those onramps and offramps only.

With the addition of linked transports and the whole new possibilities for event-flow that comes with it, Tremor has become a platform for implementing a wider variety of applications -- think servers, proxies, bridges etc., and not just ETL-style use cases. Moreover, in combination with other Tremor features and the composability that is Tremor's signature, operators can create richer applications with linked transports at the center -- think loadbalancers, or custom APIs that dynamically change pipeline behaviour (without the need for pipeline redeploy).

This document will describe the feature with concrete examples next, so if the above possibilities seem abstract to you, we hope it will be more clear by the end here.

## Basic configuration

The linked behavior for an onramp or offramp can be turned on by setting the `linked` config param for the artefact to `true` (by default, it's `false`). A simple Tremor deployment illustrating the feature:

```yaml
onramp:
  - id: websocket
    type: ws
    # turns on linked transport for this ramp
    linked: true
    codec: string
    preprocessors:
      # events are delimited by new line
      - lines
    postprocessors:
      - lines
    config:
      host: localhost
      port: 8139

binding:
  - id: echo
    links:
      # send incoming event from a websocket connection to the built-In
      # passthrough pipeline
      "/onramp/websocket/{instance}/out":
        ["/pipeline/system::passthrough/system/in"]

      # and now send back the event from the same websocket connection
      "/pipeline/system::passthrough/system/out":
        ["/onramp/websocket/{instance}/in"]

mapping:
  /binding/echo/01:
    instance: "01"
```

This instantiates a websocket server that listens to (new-line delimited) events on port 8139. After an event comes through a client websocket connection, it goes to the built-in passthrough pipeline, and is then sent back out to the client from the same connection.

We have now in our hands a classic websocket echo server! You can test the functionality with a tool like [websocat](https://github.com/vi/websocat).

```sh
# we see the same message echoed back \o/
$ echo "hello" | websocat -n1 ws://localhost:8139
hello
```

The offramp linking works similarly, with the offramp `out` port capturing the event coming back as a reply to the event transmitted to the external sink (examples of this in action are detailed below).

## Supported ramps

Ramp artefacts that support linked transports are listed here:

* [REST Onramp](../artefacts/onramps.md#rest)
* [REST Offramp](../artefacts/offramps.md#rest)
* [Websocket Onramp](../artefacts/onramps.md#ws)
* [Websocket Offramp](../artefacts/onramps.md#ws)
* [Discord onramp](../artefacts/onramps.md#discord)
* [KV offramp](../artefacts/offramps.md#kv)

As part of the above docs, you will also find event metadata variables that these onramps/offramps set (and use), which can be utilized as part of the wider application built using these aretefacts.

## Example use cases

In the above example, instead of using a passthrough pipeline, you can imagine processing the incoming event from a custom trickle pipeline, with the various [operators](../tremor-query/operators.md) we have at our disposal. In this vein, more elaborate server examples based on onramp linking (and supporting request/response style interactions) are linked below:

* [HTTP server](../workshop/examples/30_servers_lt_http/README.md)
* [Websocket server](../workshop/examples/31_servers_lt_ws/README.md)

When linked onramps of this sort are coupled with linked offramps, we have proxy applications, where incoming requests from clients can be forwarded to upstream servers and the resulting response can then be returned back to the client which initiated the request. Custom proxying logic (eg: deciding the upstream based on incoming request attributes) can be coded up as part of the [runtime script](../tremor-query/operators.md#runtimetremor). Some concrete examples demonstrating this pattern:

* [HTTP Proxy](../workshop/examples/32_proxies_lt_http/README.md)
* [Websocket Proxy](../workshop/examples/33_proxies_lt_ws/README.md)

??? example "Example binding for a HTTP proxy"
    ```yaml
    - id: main
      links:
        # send incoming requests for processing
        "/onramp/http/{instance}/out":
          ["/pipeline/request_processing/{instance}/in"]

        # process incoming requests and relay it to upstream
        "/pipeline/request_processing/{instance}/out":
          ["/offramp/upstream/{instance}/in"]

        # send the response from upstream for processing
        # (here be linked offramp)
        "/offramp/upstream/{instance}/out":
          9["/pipeline/response_processing/{instance}/in"]

        # process upstream response and send it back as a response to incoming
        # (here be linked onramp)
        "/pipeline/response_processing/{instance}/out":
          ["/onramp/http/{instance}/in"]
    ```

And when proxying, if we configure linked onramps and offramps of different types, we have bridges:

* [HTTP -> WS Bridge](../workshop/examples/34_bridges_lt_http_ws/README.md)

Or when the proxying use case is combined with some qos operators ([roundrobin](../tremor-query/operators.md#qosroundrobin) and [backpressure](../tremor-query/operators.md#qosbackpressure)), we get a working load-balancer:

* [HTTP Load Balancing](../workshop/examples/35_reverse_proxy_load_balancing/README.md)

These are some example use cases now possible with linked transports at the center, but with the amount of flexibility and composability that Tremor supports for its various capabilities, we can get very creative with what we can do here -- our imagination is the limit.

Examples of even more advanced Tremor applications:

* [Quota Service](../workshop/examples/36_quota_service/README.md)
* [Configurator](../workshop/examples/37_configurator/README.md)

## Error handling

The above linked examples also demonstrate typical error handling needed for applications built on top of linked transports (eg: for HTTP-based applications, how to send a proper error response to the client with an appropriate status code on tremor-internal failures like runtime script errors, or codec errors on invalid input).

??? example "Example error-handling binding for a HTTP proxy"
    ```yaml
    - id: error
      links:
        "/onramp/http/{instance}/err":
          ["/pipeline/internal_error_processing/{instance}/in"]

        "/pipeline/request_processing/{instance}/err":
          ["/pipeline/internal_error_processing/{instance}/in"]

        "/offramp/upstream/{instance}/err":
          ["/pipeline/internal_error_processing/{instance}/in"]

        "/pipeline/response_processing/{instance}/err":
          ["/pipeline/internal_error_processing/{instance}/in"]

        # send back errors as response as well
        "/pipeline/internal_error_processing/{instance}/out":
          ["/onramp/http/{instance}/in"]

        # respond on errors during error processing too
        "/pipeline/internal_error_processing/{instance}/err":
          ["/onramp/http/{instance
    ```

The key here is remembering to link the error ports for all the onramp/offramp/pipeline artefacts involved in the main event-flow, ensuring that the end destination for error events (emitted from the `err` ports) are visible to the client (or user).

## Correlation

If requests to and responses from a linked transport need to be correlated, the special metadata field `$correlation` can be used. It will be forwarded from the request event to the response event, so that some data from the request can be present in the response context.

Example pipeline:

```trickle
define script correlate
script
  let $correlation = event.correlation_id;
  let event = patch event of erase "correlation_id" end;
  event
end;

create script correlate;

select event from in into correlate;
select event from correlate into out;
select event from correlate/err into err;
```

This script within the pipeline file above will erase `correlation_id` from the event and put it into the `$correlation` metadata. It will be available in the response pipeline, also as `$correlation`.

If both events need to be fully present and `$correlation` is only used for having a common unique identifier to bring them both together, a windowed select statement with a group by clause can help:

```trickle
define tumbling window window_size_2
with
  size = 2
  # eviction_period = ...
end;

select aggr::win::collect_flattened({
  "event": event,
  "meta": $
}) from in[window_size_2] group by $correlation into out;
```

This pipeline will output both request and response as 2-element array:

```js
[{"event": {}, "meta": {"correlation": "123456"}}, {"event": {}, "meta": {"correlation": "123456"}}]
```

## Future work

v0.9.0 introduces linked transports as a feature preview. There are known rough edges and issues with the current mode of configuring linked transports, and also how the richer, linked-transports-powered capabilities interface with rest of Tremor configuration. Some known items for future work, aimed at improving the overall usability:

* Improve the LT port linking for onramps/offramps (`onramp/in` and `offramp/out` are not natural there)
* Resolve the boilerplate involved in various aspects of LT use (eg: error handling, pipeline flow, server code)
* Simplify scatter-gather workflows
* Guaranteed delivery of events between pipelines
* Allow certain meta-variables (eg: rate/cardinality) to be set dynamically
* Better namespacing/sharing for meta-variables
