## Command Line Testing
<!-- .slide: data-background="#FF7733" -->

Writing command style tests with tremor

>>>

### Create a container hierarchy for our suite

```shell
$ mkdir tests
$ mkdir tests/command
$ echo '[ "cmd" ]' > tests/command/tags.json
$ echo '[ "all" ]' > tests/tags.json
cat <<DATA
{
    "kind": "Command",
    "includes": "**/command.yml"
}
DATA > tests/command/meta.json
```

<div style='font-size: 20px'>
We can create tags files in any directory called `tags.json` that
are a list of strings that we can use to include or exclude tests
from the test search path.  The `meta.json` file instructs tremor
that the directory structure is for an command style test.
</div>

---

#### Verify:  Container with no tests

![Verify test hierarchy](./assets/test-command-01.gif)

```shell [1-2|3-4]
# Docker based invocation
$ trecker test command /pwd/tests
# Local execution
$ tremor test command tests
```

>>>

### Test: Environment variables

```shell
$ mkdir tests/integration/env-example
```

---

### Logic: Environment variables

```yaml
name: Interrogate the environment via the env command
tags:
  - docker
suites:
  - name: Find the env for this test environment
    cases:
      - name: |
          Use env to query the environment
        command: /usr/bin/env
        tags:
          - env
        status: 0
        expects:
          - source: stdout
            contains:
              - TREMOR_PATH
```

---

### Running: Environment variables

![Verify environment variables](./assets/test-command-02.gif)

>>>


### Test: Environment Executables

```shell
$ mkdir tests/integration/which-example
```

---

### Logic: Environment Executables

```yaml
name: Use which command directly via bash sub-shell
tags:
  - cmd
  - docker
suites:
  - name: which tremor
    cases:
      - name: |
          Assert that the `tremor` binary is not on the path
        command: /bin/bash -c 'which tremor && echo "ko" || echo "ok"'
        tags:
          - which
        status: 0
        expects:
          - source: stdout
            contains:
              - ok
```

---

### Refactor: Beware `docker` vs `local` issues


![Beware env issues](./assets/test-command-03.gif)

---

### Refactor: Fix via using helper scripts?

```yaml
name: Interrogate the environment via the env command
tags:
  - docker
suites:
  - name: Find the env for this test environment
    cases:
      - name: |
          Assert that the `tremor` binary is not on the path
        command: /bin/bash check.sh
        tags:
          - which
        status: 0
        expects:
          - source: stdout
            contains:
              - ok
```

---

### Helper Script: Vary behaviour depending in environment

```shell
#!/bin/bash
# File: check.sh

if [ "$HOME" == "/root" ] ;
then
  # We are in a docker-like env - no tremor on path
  which tremor && echo "ko" || echo "ok"
else
  # we are in a mac-like env - we expect tremor on path
  which tremor && echo "ok" || echo "ko"
fi
```

---

### Running: Works `local` or in `docker`

![Env agnostic tests](./assets/test-command-04.gif)

---

### Running: Works `local` or in `docker`

```shell
# ok
trecker test command /pwd/tests
# not ok
tremor test command /pwd/tests
```

>>>

### Test: Fetch `robot.txt` via `curl`


```shell
$ mkdir tests/integration/robot-example
```


<div style='font-size: 20px'>
Hint: We assume `curl` is on the path in docker and locally!
</div>

---

### Logic: Use curl to get remote files

```yaml
name: Fetch a `robots.txt` via curl
tags:
  - curl
  - robots.txt
suites:
  - name: Download robots.txt from www.cncf.io
    cases:
      - name: curl https://www.cncf.io/robots.txt
        command: curl -vvv -o - https://www.cncf.io/robots.txt
        tags:
          - cncf.io
        status: 0
        expects:
          - source: stdout
            contains:
              - Allow
              - Disallow
              - User-agent
              - Sitemap
          - source: stderr
            contains:
              - HTTP/2 200
```

---

### Running: Curl based fetch command test

![Download robots.txt](./assets/test-command-05.gif)

>>>

### Optionally execute processes before

As with integration style tests, dependant
processes can be launched before command test
runs

```shell
mkdir tests/command/structured
```

---

### Add a `before.json`


```json
{
  "run": "tests/command/structured/before",
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
$ tree tests/command/structured/before
./tests/command/structured/before
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

---

### Verify before process

```shell
$ cd tests/command/structured/before
$ trecker server run -f /pwd/config.yaml /pwd/server.yaml /pwd/ws.trickle
```

<div style='font-size: 20px'>
Hint: You will need to `docker ps` and `docker stop` to kill the process
</div>

>>>

### Optionally execute processes after

As with integration style tests, dependent
processes can be launched after command test
runs have completed

```shell
mkdir tests/command/structured
```

<div style='font-size: 20px'>
Hint: Skip this command if you followed the `before` walkthrough
</div>

---

### Optionally execute processes after

```json
{
  "run": "tests/commands/structured/after",
  "cmd": "bash",
  "args": [
    "./after/stop.sh"
  ]
}
```

---

### Requires an `after` sub-folder

```shell
$ tree tests/commands/structured/after
./tests/commands/structured/after
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
# include `foo`, exclude `bar` command tests
$ tremor test command tests -i foo -e bar
# include `bar`, exclude `foo` command tests
$ tremor test command tests -i bar -e foo
# include `all` command tests
$tremor test command tests
# include `all` tests of all kinds
$ tremor test all tests
```

>>>

### Further reading

* [`tremor test ...`](https://docs.tremor.rs/operations/cli/#test)
* [Github - Tremor Client tests](https://github.com/tremor-rs/tremor-runtime/tree/main/tremor-cli/tests/cli)
* [Github - Tremor API via curl](https://github.com/tremor-rs/tremor-runtime/tree/main/tremor-cli/tests/api)
* [Github - Tremor API via cli](https://github.com/tremor-rs/tremor-runtime/tree/main/tremor-cli/tests/api-cli)

>>>
### End of `command test` guide
<!-- .slide: data-background="#33FF77" -->

This is the end of the command test getting started guide

Note: This will only appear in speaker notes window
