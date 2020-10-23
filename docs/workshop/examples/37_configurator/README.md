# Configurator

An application built using tremor (and the new [linked transports](../../../operations/linked-transports.md) feature new in 0.9) allowing for centralized configuration across services and their component nodes.

This is an exploration project meant to push what we can do with the current tremor feature set and as such, there are/will be rough edges.

## Setup

!!! note
    All the application code here is available from the docs [git repository](https://github.com/tremor-rs/tremor-www-docs/tree/main/docs/workshop/examples/37_configurator).

```sh
# start everything
docker-compose up
```

Following services should be now accessible:

* Configurator: [http://localhost:9139](http://localhost:9139)
* [Quota Service](../36_quota_service/README.md) Node 1: [http://localhost:8139](http://localhost:8139)
* [Quota Service](../36_quota_service/README.md) Node 2: [http://localhost:8140](http://localhost:8140)

## Using the Configurator

**List routes**

```sh
$ curl http://localhost:9139

      Welcome to the Configurator!

      Available routes:

      GET /services
      POST /service/<id>

      HEAD /ping
      GET /stats

      /echo
```

**List services**

```sh
$ curl http://localhost:9139/services

  ["quota_service]
```

**Set service configuration**

```sh
# change quotas for the quota service
$ curl -XPOST -H'Content-Type: application/json' http://localhost:9139/service/quota_service -d'{"application_default": 11}'

# should have now applied to all the nodes in the quota service.
# if the delivery fails on a node (eg: it's down or there's network issues), it will be retried until it's successful
# (this works even if the configurator gets restarted during the process, since the undelivered updates are stored on disk)

$ curl http://localhost:8139/quotas
{"host_default":500,"logger_default":50,"tremolo":100,"index_default":100,"application_default":11}

$ curl http://localhost:8140/quotas
{"host_default":500,"logger_default":50,"tremolo":100,"index_default":100,"application_default":11}
```

**Debug request**

```sh
$ curl -XPOST localhost:9139/echo -d'{"snot": "badger"}'

{"body":"{\"snot\": \"badger\"}","meta":{"method":"POST","headers":{"content-length":["18"],"content-type":["application/x-www-form-urlencoded"],"user-agent":["curl/7.65.3"],"accept":["*/*"],"host":["localhost:9139"]},"url":{"scheme":"http","host":"localhost","port":9139,"path":"/echo"}}}
```

## TODO

* aggregate responses from service constituents (from tremor-script for now)
* explore pull model for configuration sync
* generate per-service config routes from openapi specs
* templatize new service addition/boilerplate

In the context of configuring tremor nodes, problems around configuration sync/distribution will be easier to solve after tremor becomes truly clustered, but for now, we can try and tackle it with what we have and see how far we go (eg: via guaranteed delivery or periodic updates).
