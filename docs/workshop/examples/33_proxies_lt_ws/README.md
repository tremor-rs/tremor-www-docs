# Websocket Proxy

Example Websocket proxy application built on top of Tremor and meant to be a demonstration of [linked transports](../../../operations/linked-transports.md).

## Setup

!!! tip
    All the code here is available in the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/33_proxies_lt_ws) as well.

### Sources and sinks

We configure a websocket onramp listening on port 9139, that is meant to be a proxy for our [example websocket server](../31_servers_lt_ws/README.md) (configured as en endpoint in the websocket offramp here).

```yaml
onramp:
  - id: ws
    type: ws
    linked: true
    codec: string
    preprocessors:
      - lines
    config:
      host: 0.0.0.0
      port: 9139

offramp:
  - id: upstream
    type: ws
    linked: true
    codec: string
    postprocessors:
      - lines
    config:
      url: "ws://tremor-server:8139"
```

### Message flow

Incoming websocket messages from a client's websocket connection are forwarded to the upstream websocket server (via the `pass_incoming` pipeline which just lives up to its name). The resulting upstream reply is then returned back to the client reusing its connection (after a quick pass through the `pass_outgoing` pipeline).

```yaml
binding:
  - id: main
    links:
      "/onramp/ws/{instance}/out":
        ["/pipeline/pass_incoming/{instance}/in"]

      "/pipeline/pass_incoming/{instance}/out":
        ["/offramp/upstream/{instance}/in"]

      "/offramp/upstream/{instance}/out":
        ["/pipeline/pass_outgoing/{instance}/in"]

      "/pipeline/pass_outgoing/{instance}/out":
        ["/onramp/ws/{instance}/in"]
```

### Processing logic

Implementation for the `pass_incoming` (as well as `pass_outgoing`) pipeline:

```trickle
select event from in into out;
```

This example is intentionally light on the processing but you can imagine doing arbitrary processing based on the event data here (as well as dynamically changing the confiuration for the [websocket offramp](../../../artefacts/offramps.md#ws) via its metadata variables --  eg: things like the server url).

## Testing

Assuming you have all the code from the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/33_proxies_lt_ws), run the following to start our application (along with the [tremor websocket server example](../31_servers_lt_ws/README.md) that is the upstream for our proxy):

```sh
docker-compose up
```

Now let's try to test the echo capabilities of our upstream server, via a tool like [websocat](https://github.com/vi/websocat).

!!! note
    Can be installed via `cargo install websocat` for the lazy/impatient amongst us

```sh
# via proxy
$ echo "hello" | websocat -n1 ws://localhost:9139
hello

# just the upstream
$ echo "hello" | websocat -n1 ws://localhost:8139
hello
```

Our special snot-handling works as well:

```sh
$ echo "snot" | websocat -n1 ws://localhost:9139
badger
```

And if there's an internal tremor error while processing both the incoming message and the upstream reply to it (eg: codec or pre/post-processor failure), or if the upstream server is just down, an error will be bubbled up to the client. Example:

```sh
# stop the upstream server
$ docker stop 33_proxies_lt_ws_tremor-server_1

# upstream connection now gets closed from the proxy
$ echo "hello" | websocat -n1 ws://localhost:9139
{"error":"Error receiving reply from server ws://localhost:8139: WebSocket protocol error: Connection reset without closing handshake","event_id":"
1: 2"}

# sending further messages results in errors
$ echo "hello" | websocat -n1 ws://localhost:9139
$ echo "hello" | websocat -n1 ws://localhost:9139
{"error":"Error sending event to server ws://localhost:8139: Trying to work with closed connection","event_id":"1: 3"}
```
