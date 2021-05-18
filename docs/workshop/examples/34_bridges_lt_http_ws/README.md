# HTTP -> Websocket Bridge

Example HTTP -> Websocket bridge application built on top of Tremor and meant to be a demonstration of [linked transports](../../../operations/linked-transports.md).

## Setup

!!! tip
    All the code here is available in the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/34_bridges_lt_http_ws) as well.

### Sources and sinks

We configure a rest onramp listening on port 9139, that is meant to be a bridge for our [example websocket server](../31_servers_lt_ws//README.md) (configured as en endpoint in the websocket offramp here).

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
  - id: ws
    type: ws
    linked: true
    codec: string
    postprocessors:
      - lines
    config:
      url: "ws://tremor-server:8139"
```

### Request flow

Incoming HTTP requests from clients are forwarded to the `request_processing` pipeline, from where it goes to the websocket server. The resulting websocket message reply is then sent back as HTTP response to the client which initiated the request (after some needed processing from the `response_processing` pipeline).

```yaml
binding:
  - id: main
    links:
      # send incoming requests for processing
      "/onramp/http/{instance}/out":
        ["/pipeline/request_processing/{instance}/in"]

      # process incoming requests and relay it to ws offramp
      "/pipeline/request_processing/{instance}/out":
        ["/offramp/ws/{instance}/in"]

      # send the response from ws offramp to the passthrough pipeline
      # this works well as long as the passthrough pipeline is not used
      # by anything else (which is the case for this example)
      "/offramp/ws/{instance}/out":
        ["/pipeline/response_processing/{instance}/in"]

      # send the ws repsonse back as a response to incoming
      "/pipeline/response_processing/{instance}/out":
        ["/onramp/http/{instance}/in"]
```

### Processing logic

Implementation for the `request_processing` pipeline:

```trickle
define script process
script
  match $request.url.path of
    # only pass requests to /bridge
    case "/bridge" =>
      null
    default =>
      # can send this to a different port than the default err port too
      emit {
        "error": "Unsupported url path: {$request.url.path}",
        "event": event
      } => "err"
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

Implementation for the `response_processing` pipeline:

```trickle
define script process
script
  # defaults for the server response
  let $response = {
    "status": 200,
    "headers": {
      "x-powered-by": "Tremor",
    }
  };
  event;
end;

create script process;

# main request processing
select event from in into process;
select event from process into out;

# tremor runtime errors from the processing script
select event from process/err into err;
```

## Testing

Assuming you have all the code from the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/34_bridges_lt_http_ws), run the following to start our application (along with the [tremor websocket server example](../31_servers_lt_ws/README.md) that our application is bridging to):

```sh
docker compose up
```

Now let's try to test the echo capabilities of the websocket server example, via the HTTP bridge:

```sh
# via the HTTP bridge
$ curl -i http://localhost:9139/bridge -d "hello"
HTTP/1.1 200 OK
content-length: 5
date: Thu, 15 Oct 2020 05:24:23 GMT
content-type: text/plain
x-powered-by: Tremor

hello


# just the websocket server
$ echo "hello" | websocat -n1 ws://localhost:8139
hello
```

Our special snot-handling works as well:

```sh
$ curl -i http://localhost:9139/bridge -d "snot"
badger
```

Only the `/bridge` path (as setup from the pipeline) works for the bridging:

```sh
$ curl http://localhost:9139/some_path -d "snot"
{"error":"Oh no, we ran into something unexpected :(\n Unsupported url path: /some_path","event":"snot"}
```

And if there's an internal tremor error while processing both the incoming HTTP request and the websocket reply to it (eg: codec or pre/post-processor failure), or if the websocket server is just down, an error will be bubbled up to the client. Example:

```sh
# stop the websocket server
$ docker stop 34_bridges_lt_http_ws_tremor-server_1

# websocket server connection now gets closed from the bridge
$ curl -i http://localhost:9139/bridge -d "hello"
HTTP/1.1 500 Internal Server Error
content-length: 198
date: Fri, 16 Oct 2020 04:12:11 GMT
content-type: application/json

{"error":"Oh no, we ran into something unexpected :(\n Error receiving reply from server ws://localhost:8139: WebSocket protocol error: Connection reset without closing handshake","event_id":"1:0:3"}

Internally the websocket offramp is trying to re-establish the connection continuously.

Restarting the docker websocket server will heal the offramp:

```sh
# restart the websocket server
$ docker start 34_bridges_lt_http_ws_tremor-server_1

$ curl http://localhost:9139/bridge -d "hello"
hello
```
