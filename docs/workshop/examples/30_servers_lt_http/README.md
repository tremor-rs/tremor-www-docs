# Server Applications

Based on linked transport.

TODO add details

## HTTP Server

```sh
cd etc/tremor_http/config
TREMOR_PATH="${TREMOR_PATH}:." tremor server run -f config.yaml -f request_processing.trickle -f internal_error_processing.trickle
```

TODO add simpler server as part of the LT explanatory doc
