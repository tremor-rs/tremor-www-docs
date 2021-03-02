# HTTP Proxy

Example HTTP proxy application built on top of Tremor and meant to be a demonstration of [linked transports](../../../operations/linked-transports.md).

## Setup

!!! tip
    All the code here is available in the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/32_proxies_lt_http) as well.

### Sources and sinks

We configure a rest onramp listening on port 9139, that is meant to be a proxy for our [example HTTP server](../30_servers_lt_http/README.md) (configured as en endpoint in the rest offramp here).

```yaml
onramp:
  - id: http
    type: rest
    linked: true
    codec: string
    config:
      host: 0.0.0.0
      port: 9139

offramp:
  - id: upstream
    type: rest
    linked: true
    codec: string
    config:
      endpoint:
        host: tremor-server
        port: 8139
```

### Request flow

Incoming requests from clients are forwarded to the `request_processing` pipeline, from where it goes to the upstream server. The resulting response is then returned back to the client which initiated the request (after any needed processing from the `response_processing` pipeline).

```yaml
binding:
  - id: main
    links:
      # send incoming requests for processing
      "/onramp/http/{instance}/out":
        ["/pipeline/request_processing/{instance}/in"]

      # process incoming requests and relay it to upstream
      "/pipeline/request_processing/{instance}/out":
        ["/offramp/upstream/{instance}/in"]

      # send the response from upstream for processing
      "/offramp/upstream/{instance}/out":
        ["/pipeline/response_processing/{instance}/in"]

      # process upstream response and send it back as a response to incoming
      "/pipeline/response_processing/{instance}/out":
        ["/onramp/http/{instance}/in"]
```

### Processing logic

Implementation for the `request_processing` pipeline:

```trickle
define script process
script
  # erase the host/port from request url so that requests are routed
  # to the endpoint configured as part of the rest offramp
  # can set endpoint concretely here too, depending on the need
  # (eg: different endpoint based on request path/headers)
  let $endpoint = patch $request.url of
    erase "host",
    erase "port"
  end;
  event;
end;

create script process;

# main request processing
select event from in into process;
select event from process into out;

# tremor runtime errors from the processing script
select event from process/err into err;
```

This example demonstrates the minimal processing needed for the proxying logic to work, but you can do any arbitrary processsing on the incoming request as needed (eg: deciding a different upstream based on certain incoming request attributes like headers or request paths).

The [response_processing](etc/tremor/config/response_processing.trickle) pipeline is similarly minimal -- it just adds an entry to the `x-powered-by` header for showing response modifications (if you don't need it, you can just use a passthrough pipeline, or even rely on the default `system::passthrough` pipeline which eliminates the need to create this new pipeline).

## Testing

Assuming you have all the code from the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/32_proxies_lt_http), run the following to start our application (along with the tremor http server example that is the upstream for our proxy):

```sh
docker-compose up
```

Now let's try to access an endpoint that we know is available in the upstream server:

```sh
# via the proxy. note the additional entry we have in the x-powered-by header
$ curl -i http://localhost:9139/snot
HTTP/1.1 200 OK
content-length: 8
x-powered-by: Tremor, Tremor (As Proxy)
content-type: application/json
date: Thu, 15 Oct 2020 05:00:06 GMT

"badger"


# just the upstream
$ curl -i http://localhost:8139/snot
HTTP/1.1 200 OK
content-length: 8
date: Thu, 15 Oct 2020 05:00:44 GMT
content-type: application/json
x-powered-by: Tremor

"badger"
```

All the [testing examples](../30_servers_lt_http/README.md#testing) for the example HTTP server should work from here as well, with the port `8139` there swapped to our proxy application port `9139`.
