# Tremor setup for feeding data into a Kafka cluster

Start with:

```sh
tremor server run -f 00_ramps.yaml 01_binding.yaml 02_mapping.yaml -l ../logger.yaml
```
