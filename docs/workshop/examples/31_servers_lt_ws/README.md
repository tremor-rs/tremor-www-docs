# Websocket Server

Example Websocket server application built on top of Tremor and meant to be a demonstration of [linked transports](../../../operations/linked-transports.md).

## Setup

!!! tip
    All the code here is available in the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/31_servers_lt_ws) as well.

### Sources

We configure a websocket onramp listening on port 8139:

```yaml
  - id: ws
    type: ws
    linked: true
    codec: string
    preprocessors:
      - lines
    config:
      host: 0.0.0.0
      port: 8139
```

### Message flow

Incoming websocket messages from a client's websocket connection are sent to the pipeline `echo` and the output of it is sent back again from the same connection.

```yaml
binding:
  - id: main
    links:
      "/onramp/ws/{instance}/out": ["/pipeline/echo/{instance}/in"]
      "/pipeline/echo/{instance}/out": ["/onramp/ws/{instance}/in"]
```

### Processing logic

Implementation for the `echo` pipeline (techincally, echo with one special twist):

```trickle
define script process
script
  match event of
    # snot is a special snowflake
    case "snot" => "badger"
    default => event
  end
end;

create script process;

# main request processing
select event from in into process;
select event from process into out;

# tremor runtime errors from the processing script
select event from process/err into err;
```

## Testing

Assuming you have all the code from the [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/31_servers_lt_ws), run the following to start our application:

```sh
docker-compose up
```

Test the websocket server with a tool like [websocat](https://github.com/vi/websocat).

!!! note
    Can be installed via `cargo install websocat` for the lazy/impatient amongst us

```sh
# anything you type and enter, will be echoed back
# except snot which begets badger
$ websocat ws://localhost:8139
hello
hello
world
world
snot
badger
goodbye
goodbye
```

If there's internal tremor error while processing the incoming message (eg: codec or preprocessor failure), the error should be bubbled up to the client. To test this out, change the codec in the [onramp configuration](etc/tremor/config/config.yaml) to be `json` from `string` and send an invalid json input:

```sh
# after changing the onramp codec to json
$ echo "{" | websocat -n1 ws://localhost:8139
{"error":"[Codec] Syntax at character 0 ('{')","event_id":1,"source_id":"tremor://localhost/onramp/ws/01/in"}
```
