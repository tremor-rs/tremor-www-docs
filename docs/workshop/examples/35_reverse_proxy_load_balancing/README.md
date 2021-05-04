# Reverse proxy with Load Balancing

This example shows how to setup tremor as a reverse proxy for HTTP/1.1 that
load balances between multiple upstream servers in a round-robin fashion.

We are going to make use of the new [linked transport](../../../operations/linked-transports.md) and *Quality of Service* features in tremor *0.9*.

## Setting up multiple web-servers for testing purposes

We use the server behind `https://httpbin.org` to have three endpoints ready to proxy to and to inspect what we sent vs. what the upstream servers received.

Three httpbin servers are set up in the accompagnying `docker-compose.yml`.

## Setting up Tremor as a reverse proxy

!!! tip
    All the code here is available in the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/35_reverse_proxy_load_balancing) as well.


To issue incoming HTTP requests to an upstream HTTP server
a [REST onramp](../../../artefacts/onramps.md#rest) needs to be configured in `config.yaml` to listen on a port of our choice:

```yaml
onramp:
    - id: http_in
      type: rest
      linked: true # with this (new) setting, this onramp will be able to receive and send out responses to each request
      codec: json
      config:
        host: 0.0.0.0
        port: 65535
```

To forward received requests to the httpbin upstream servers a [REST offramp](../../../artefacts/offramps.md#rest) needs to be configured in `config.yaml` to point at each of it:

```yaml
offramp:
    - id: upstream01
      type: rest
      linked: true
      codec: json
      config:
        endpoint:
          host: webserver01
        concurrency: 9 # allo max 9 concurrent in-flight requests
    - id: upstream02
      type: rest
      linked: true
      codec: json
      config:
        endpoint:
          host: webserver02
        method: POST # set a default method if no $request.method is set
    - id: upstream03
      type: rest
      linked: true
      codec: json
      config:
        endpoint:
          host: webserver03
        headers: # add some headers
          "X-Upstream": "upstream03"
```

Then we need to do the actual proxying in a pipeline that receives requests from the `http_in` onramp, inspects it, manipulates it and forwards it to one of the configured offramps:

```trickle
define script request_handling
script
    let host = match $request.headers of
      case %{ present host } => $request.headers.host[0]
      default => "UNDEFINED"
    end;
    let forwarded = "by=localhost:65535;host={host};proto=http";
    let $request.headers["Forwarded"] = forwarded;

    # fiddle with the event
    let event = patch event of
      insert "forwarded" => forwarded
    end;

    # set request url parts for forwarding it to the rest offramp
    # stripping out the host and port, as they will be set by the offramp
    let $endpoint = patch $request.url of
      erase "host",
      erase "port"
    end;

    event;
end;

# ensure we distribute the load evenly
define qos::roundrobin operator rr
with
  outputs = ["ws01", "ws02", "ws03"]
end;
create operator rr;

# apply backpressure if a server cannot keep up
# or is not reachable
define qos::backpressure operator bp
with
  timeout = 10000, # max timeout before triggering this operator - 10s
  steps = [100, 500, 1000, 10000] # backoff steps in ms
end;
create operator bp01 from bp;
create operator bp02 from bp;
create operator bp03 from bp;

create script request_handling;

# wire everything together
select event from in into request_handling;
select event from request_handling into rr;
# connect each upstream throught the round-robin operator and a distinct backpressure operator
select event from rr/ws01 into bp01;
select event from rr/ws02 into bp02;
select event from rr/ws03 into bp03;
# create three outputs - one for each upstream server
select event from bp01 into out/ws01;
select event from bp02 into out/ws02;
select event from bp03 into out/ws03;
select event from request_handling/err into err; # report error to its own port
```

With the `qos::roundrobin` and `qos::backpressure` we distribute the load evenly and
back off if a server is overloaded or events continue to fail (result in HTTP status coded >= 400 or are unable to establish a connection etc.).

But this is only half a proxy without response handling getting back from the offramp, which is only now possible with the dawn of [linked transports](../../../operations/linked-transports.md). Handling the responses coming back from the upstreams is implemented in the following pipeline:

```trickle
define script response_handling
script
    use std::array;
    use tremor::system;
    # see: https://tools.ietf.org/html/rfc7230#section-5.7.1
    let via_value = "1.1 #{system::hostname()}/tremor";
    match $response.headers of
        case %{ present via } =>
            let $response.headers.via = array::push($response.headers.via, via_value)

        default =>
            let $response.headers.via = via_value
    end;
    event;
end;
create script response_handling;

select event from in into response_handling;
select event from response_handling into out;
select event from response_handling/err into err;
```

Here we only set the `Via` response header.

Now the single bits need to be connected in order to complete the flow back and forth between client and upstream. When linking [REST offramps](../../../artefacts/offramps.md#rest) and [onramps](../../../artefacts/onramps.md#rest) together it is important to take care that any error that might happen on the way is reported back to the REST onramp `http_in` as otherwise clients would not receive any response. Luckily with Linked Transports we can connect all error outputs easily in our binding and thus will receive proper error messages as HTTP responses.
Again, we do it in `config.yaml`:

```yaml
binding:
    - id: main
      links:
        "/onramp/http_in/{instance}/out": ["/pipeline/request_handling/{instance}/in"]
        # connect the three pipeline outputs to the offramps to our upstream servers
        "/pipeline/request_handling/{instance}/ws01": ["/offramp/upstream01/{instance}/in"]
        "/pipeline/request_handling/{instance}/ws02": ["/offramp/upstream02/{instance}/in"]
        "/pipeline/request_handling/{instance}/ws03": ["/offramp/upstream03/{instance}/in"]
        # send responses from upstreams through the response handling pipeline
        "/offramp/upstream01/{instance}/out": ["/pipeline/response_handling/{instance}/in"]
        "/offramp/upstream02/{instance}/out": ["/pipeline/response_handling/{instance}/in"]
        "/offramp/upstream03/{instance}/out": ["/pipeline/response_handling/{instance}/in"]
        # send responses back to the http_in onramp
        "/pipeline/response_handling/{instance}/out": ["/onramp/http_in/{instance}/in"]
        # error handling - send errors back to the http_in onramp
        "/pipeline/request_handling/{instance}/err": ["/onramp/http_in/{instance}/in"]
        "/pipeline/response_handling/{instance}/err": ["/onramp/http_in/{instance}/in"]
        "/offramp/upstream01/{instance}/err": ["/pipeline/internal_error_processing/{instance}/in"]
        "/offramp/upstream02/{instance}/err": ["/pipeline/internal_error_processing/{instance}/in"]
        "/offramp/upstream03/{instance}/err": ["/pipeline/internal_error_processing/{instance}/in"]
        "/pipeline/internal_error_processing/{instance}/out": ["onramp/http_in/{instance}/in"]
        "/pipeline/internal_error_processing/{instance}/err": ["onramp/http_in/{instance}/in"]
mapping:
  /binding/main/01:
    instance: "01"
```

## Start the Reverse Proxy and test it

We set up 3 upstream servers and tremor itself in the `docker-compose.yml`.
Starting them is straight-forward:

```bash
$ docker compose up
```

In another shell, we fire up curl and send requests through our reverse proxy:

```bash
$ curl -v -XGET http://localhost:65535/anything  -H'Content-Type: appliaction/json' -d '{"snot": "badger"}'
*   Trying ::1...
* TCP_NODELAY set
* Connected to localhost (::1) port 65535 (#0)
> GET /anything HTTP/1.1
> Host: localhost:65535
> User-Agent: curl/7.64.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 18
>
* upload completely sent off: 18 out of 18 bytes
< HTTP/1.1 200 OK
< content-length: 549
< access-control-allow-origin: *
< content-type: application/json
< connection: keep-alive
< server: gunicorn/19.9.0
< date: Tue, 06 Oct 2020 15:05:22 GMT
< access-control-allow-credentials: true
< via: 1.1 789e85f38adc/tremor
<
* Connection #0 to host localhost left intact
{"args":{},"data":"{\"snot\":\"badger\",\"forwarded\":\"by=localhost:65535;host=localhost:65535;proto=http\"}","files":{},"form":{},"headers":{"Accept":"*/*","Accept-Encoding":"deflate, gzip","Content-Length":"82","Content-Type":"application/json","Expect":"100-continue","Forwarded":"by=localhost:65535;host=localhost:65535;proto=http","Host":"webserver01","User-Agent":"curl/7.64.1"},"json":{"forwarded":"by=localhost:65535;host=localhost:65535;proto=http","snot":"badger"},"method":"GET","origin":"172.19.0.5","url":"http://webserver01/anything"}
```

The tremor reverse-proxy added the `forwarded` field and header to the request (See the `data` amd `headers` fields of the response body) and passed through the response body from the upstream.

In the case of an upstream failing, the `qos::backpressure` operators will kick in and discard events for the failed upstream.

Here is an example response for the case an upstream is not reachable:

```json
{"error":"ConnectFailed: failed to connect to the server","event_id":"1:0:4"}
```
