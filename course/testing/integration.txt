## Integration Testing
<!-- .slide: data-background="#FF7733" -->

Writing integration style tests with tremor

>>>

### Create a test directory structure for our tests

```shell
$ mkdir tests
$ mkdir tests/integration
$ echo '[ "integration" ]' > tests/integration/tags.json
$ echo '[ "all" ]' > tests/tags.json
cat <<DATA
{
    "kind": "Integration",
    "includes": "integration-test-*"
}
DATA > tests/integration/meta.json
```

<div style='font-size: 20px'>
We can create tags files in any directory called `tags.json` that
are a list of strings that we can use to include or exclude tests
from the test search path.  The `meta.json` file instructs tremor
that the directory structure is for an integration style test.
</div>

---

#### Verify:  `trecker test /pwd/tests`

![Verify test hierarchy](./assets/test-integration-01.gif)

```shell
$ tremor test integration tests
```

>>>

### Add a folder to contain our integration test

```shell
$ mkdir tests/integration/integration-test-01
```

>>>

### Add main trickle file for test

Add a main trickle query file for the system under test

```trickle
# File: tests/integration/integration-test-01/passthrough.trickle

select event from in into out;

```

>>>

### Config: `config.yaml` source

```yaml
# File: tests/integration/integration-test-01/config.yaml
onramp:
  - id: in
    type: file
    config:
      source: "in.json.xz"
      close_on_done: true
      sleep_on_done: 1000
```

---

### Config: `config.yaml` sink

```yaml
# File: tests/integration/integration-test-01/config.yaml
offramp:
  - id: out
    type: file
    config:
      file: "events.log"
```

---

### Config: `binding` event routes

```yaml
# File: tests/integration/integration-test-01/config.yaml
binding:
  - id: test
    links:
      "/onramp/in/{instance}/out": ["/pipeline/passthrough/{instance}/in"]
      "/pipeline/passthrough/{instance}/out": ["/offramp/out/{instance}/in"]
```

---

### Config: Instances via `mapping`

```yaml
# File: tests/integration/integration-test-01/config.yaml
mapping:
  /binding/test/1:
    instance: "1"
```

>>>

### Test Data: Record `in.json.xz`

```shell
$ cd tests/integration/integration-test-01/
$ echo '{ "snot": "badger"} ' >> in.json
echo '"tremolo" ' >> in.json
echo '1234.56 ' >> in.json
xz in.json
```

---

#### Verify: Manual test invocation

![Verify test hierarchy](./assets/test-integration-02.gif)

```shell
$ TREMOR_PATH=/path/to/tremor-script/lib tremor test integration tests
```

---

### Verify: Equivalent manual invocation

```shell
$ cd tests/integration/integration-test-01
$ tremor server run -f config.yaml passthrough.trickle
tremor version: 0.9.0
tremor instance: tremor
rd_kafka version: 0x000000ff, 1.5.0
allocator: snmalloc
Listening at: http://0.0.0.0:9898
```

---

### Test Data: Sanity check output

```shell
$ cd tests/integration/integration-test-01
$ cat events.log
{"snot":"badger"}
"tremolo"
1234.56
$ cp events.log expected.txt # if ok, use for assertions
```

>>>

### Assertions: Add `assert.yaml`

```yaml
status: 0
name: Query passthrough  assertions
asserts:
  - source: events.log # generated during run
    equals_file: expected.txt # hand crafted
    contains: # selective
      -  "snot"
      - badger
      - tremolo
      - 1234.56
```

---

### Run integration test again

![Verify assertions](./assets/test-integration-03.gif)

>>>

### Optionally execute processes before

```json
{
  "run": "tests/integration/ws/before",
  "cmd": "tremor",
  "args": [
    "server", "run",
    "-p", "before.pid",
    "-n", "-f",
    "before/ws.trickle",
    "before/config.yaml",
    "before/server.yaml"
  ],
  "await": { "port-open": [ "4242" ] },
  "max-await-secs": 15
}
```

---

### Requires a `before` sub folder for test

```shell
$ tree tests/integration/integration-test-01/before
./tests/integration/integration-test-01/before
├── config.yaml
├── server.yaml
└── ws.trickle
```

---

### Before: `config.yaml`

```yaml
onramp:
  - id: ws-in
    type: ws
    codec: json
    config:
      host: 127.0.0.1
      port: 4242

offramp:
  - id: out
    type: file
    codec: json
    config:
      file: "gen.log"
  - id: exit
    type: exit

binding:
  - id: main
    links:
      "/onramp/ws-in/{instance}/out": ["/pipeline/ws/{instance}/in"]
      "/pipeline/ws/{instance}/out": ["/offramp/out/{instance}/in" ]
      "/pipeline/ws/{instance}/exit": ["/offramp/exit/{instance}/in" ]
```

---

### Before: `server.yaml`

```yaml
mapping:
  /binding/main/1:
    instance: "1"
```

---

### Before: `ws.trickle`

```trickle
create stream quit;

select event from in
where event != "quit" into out;

select { "done": true } from in
where event == "quit" into out;

select { "exit": 0, "delay": 10000 } from in
where event == "quit" into out/exit;
```

>>>

### Optionally execute processes after

```json
{
  "run": "tests/integration/integration-test-01/after",
  "cmd": "bash",
  "args": [
    "./after/stop.sh"
  ]
}
```

---

### Requires an `after` sub-folder

```shell
$ tree tests/integration/integration-test-01/after
./tests/integration/integration-test-01/after
└── stop.sh
```

---

### After: `stop.sh`

```bash
#!/bin/bash

echo "Stopping WS by sending quit json string to port 4242"
for i in {1..5};
do
  if ! $(nc -zv  localhost 4242); then
    echo '"quit"' | websocat ws://localhost:4242
  else
    echo "Killing it softly at attempt ${i}"
    break;
  fi
done;

echo "If a pid file exists, hard kill"
if test -f before.pid; then
    kill -9 $( cat before.pid )
    # Remove pid file
    rm -f before.pid
fi
```

>>>

### Tags

Use the `-i` and `-e` flags to `tremor test`

- Given: `-i foo bar`
 - Any `foo` or `bar` tagged tests

- Given: `-i foo bar -e baz bogo`
 - Any `foo` or `bar` tagged tests
 - Excluding `baz` and `bogo`

---

```shell [1-2|3-4|5-6|7-8]
# include `foo`, exclude `bar` unit tests
$ tremor test unit tests -i foo -e bar
# include `bar`, exclude `foo` unit tests
$ tremor test unit tests -i bar -e foo
# include `all` unit tests
$tremor test unit tests
# include `all` tests of all kinds
$ tremor test all tests
```

>>>

### Further reading

* [`tremor test ...`](https://docs.tremor.rs/operations/cli/#test)
* [Github - Tremor Integration tests](https://github.com/tremor-rs/tremor-runtime/tree/main/tremor-cli/tests/integration)

>>>
### End of `integration test` guide
<!-- .slide: data-background="#33FF77" -->

This is the end of the integration test getting started guide

Note: This will only appear in speaker notes window


