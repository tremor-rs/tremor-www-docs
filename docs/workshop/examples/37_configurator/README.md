# Configurator

An application built using tremor using the [linked transports](../../../operations/linked-transports.md) feature and the [qos::wal](https://docs.tremor.rs/tremor-query/operators/#qoswal) operator introduced in 0.9 and the [`$correlation`](https://docs.tremor.rs/operations/linked-transports/#correlation) feature introduced in 0.11, allowing for centralized configuration across services and their component nodes.

The main task of the Configurator is to distribute config changes to a group of upstream tremor nodes running the [_Quota Service_](../36_quota_service/README.md).
The config changes do not happen in an atomic or transactional fashion across all upstream nodes, but all valid configuration updates are persisted and retried until they succeed.
The responses are aggregated from all the upstream nodes and bundled into a single event / HTTP response.

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
      GET /service/<id>
      GET /service/<id>/...
      PUT /service/<id>/...
      DELETE /service/<id>/...

      HEAD /ping
      GET /stats

      * /echo
```

**List services**

```sh
$ curl http://localhost:9139/services

  ["quota_service"]
```

**Set service configuration**

```sh
# change a quota for all instances of the quota service
$ curl -XPUT -H'Content-Type: application/json' http://localhost:9139/service/quota_service/application_default -d'11' | jq .
[
  {
    "response": {
      "application_default": 100
    },
    "upstream": "quota_service_1"
  },
  {
    "response": {
      "application_default": 100
    },
    "upstream": "quota_service_2"
  }
]
# As the response suggests, the config update has been applied to all the nodes in the quota service.
# The config value for `application_default` has been changed from `100` to `11`.
# If the delivery fails on a node (eg: it's down or there's network issues), it will be retried until it's successful
# (this works even if the configurator gets restarted during the process, since the undelivered updates are stored on disk)
```

We can verify that the config changes got applied by checking the configu through the configurator
or through each quota_service instance:

```sh
$ curl http://localhost:9139/service/quota_service | jq .
[
  {
    "response": {
      "host_default": 500,
      "logger_default": 50,
      "index_default": 100,
      "tremolo": 100,
      "application_default": 11
    },
    "upstream": "quota_service_2"
  },
  {
    "response": {
      "host_default": 500,
      "logger_default": 50,
      "index_default": 100,
      "tremolo": 100,
      "application_default": 11
    },
    "upstream": "quota_service_1"
  }
]

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

* explore pull model for configuration sync
* generate per-service config routes from openapi specs
* templatize new service addition/boilerplate

In the context of configuring tremor nodes, problems around configuration sync/distribution will be easier to solve after tremor becomes truly clustered, but for now, we can try and tackle it with what we have and see how far we go (eg: via guaranteed delivery or periodic updates).
