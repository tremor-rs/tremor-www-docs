# Proxy Applications

Based on linked transport.

TODO add details


## HTTP Proxy Server

```sh
# start the upstream server and keep it running
cd ../30_servers_lt/etc/tremor_http/config
TREMOR_PATH="${TREMOR_PATH}:." tremor server run --no-api -f config.yaml -f request_processing.trickle -f internal_error_processing.trickle

# start the proxy for the above server
cd etc/tremor_http/config
tremor server run -f config.yaml -f request_processing.trickle -f response_processing.trickle -f internal_error_processing.trickle
```

TODO add simple passthrough proxy as part of the LT explanatory doc
