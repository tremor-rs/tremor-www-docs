# Transform

This example demonstrates extracting data from a Postgres database and inserting
data to TimescaleDB.

The demo starts up said PostgreSQL, TimescaleDB, Tremor and `pgweb`.

## Environment

In [`00_ramps.yaml`](etc/tremor/config/00_ramps.yaml) we pass in a
configuration for an onramp of type `postgres` along with typical connection
string requirements.

Additionally, we are required to specify `interval_ms` which stands for
frequency of polling that Tremor is performing on Postgres database with the
given `query`. Query will be passed two parameters:
* `$1` is the `TIMESTAMPTZ` that indicates the start time and date for the
  range
* `$2` is the `TIMESTAMPTZ` that indicates the ending time and date for the
  range

The initial range is formed by taking `consume_from` configuration setting and
the current time and date. This will effectivelly backfill data. From then on,
Tremor will poll in regular `interval_ms`.

In addition to a `postgres` onramp, we also utilize a `crononome` onramp. The
intention is to demonstrate intermediate record format which is accepted by
`postgres` offramp.

## Business Logic

We have two pipelines.
- [`postgres.trickle`](etc/tremor/config/postgres.trickle) for data coming from a PostgreSQL database
- [`crononome.trickle`](etc/tremor/config/crononome.trickle) for events coming from the `crononome` onramp at a regular interval of `5s`.

## Command line testing during logic development

```bash
$ docker-compose up
  ... lots of logs ...
```

Open the [pgweb](http://localhost:8081) to browse through received rows in
TimescaleDB.

### Discussion
