# Codecs

Codecs are used to describe how to decode data from the wire and encode it back to wire format.

## Supported Codecs

### json

En- and decodes [JSON](https://json.org), for encoding a minified format is used (excluding newlines and spaces).

### string

Treats the event as non structured string. It is required that the input **is valid UTF-8** or the decoding will fail.

### msgpack

[Msgpack](https://msgpack.org) works based on the msgpack binary format that is structurally compatible with JSON.

Being a binary format, message pack is significantly more performant and requires less space compared to JSON.

It is an excellent candidate to use in tremor to tremor deployments but as well with any offramp that does support this format.

### influx

En- and decodes the [influx line protocol](https://docs.influxdata.com/influxdb/v1.7/write_protocols/line_protocol_tutorial/). The structural representation of the data is as follows:

```text
weather,location=us-midwest temperature=82 1465839830100400200
```

translates to:

```json
{
  "measurement": "weather",
  "tags": { "location": "us-midwest" },
  "fields": { "temperature": 82.0 },
  "timestamp": 1465839830100400200
}
```

### binflux

The `binflux` codec is a binary representation of influx data that is significantly faster encodes and decodes as well as takes less space on the wire.

The format itself does not include framing but can be used with the `size-prefix` pre/post processors.

For all numbers network byte order is used (big endian). The data is represented as follows:

1. _2 byte_ (u16) length of the `measurement` in bytes
2. _n byte_ (utf8) the measurement (utf8 encoded string)
3. _8 byte_ (u64) the timestamp
4. _2 byte_ (u16) number of tags (key value pairs) repetitions of:
   1. _2 byte_ (u16) length of the tag name in bytes
   2. _n byte_ (utf8) tag name (utf8 encoded string)
   3. _2 byte_ (u16) length of tag value in bytes
   4. _n byte_ (utf8) tag value (utf8 encoded string)
5. _2 byte_ (u16) number of fiends (key value pairs) repetition of:
   1. _2 byte_ (u16) length of the tag name in bytes
   2. _n byte_ (utf8) tag name (utf8 encoded string)
   3. _1 byte_ (tag) type of the field value can be one of:
   4. `TYPE_I64 = 0` followed by _8 byte_ (i64)
      1. `TYPE_F64 = 1` followed by _8 byte_ (f64)
      2. `TYPE_TRUE = 2` no following data
      3. `TYPE_FALSE = 3` no following data
      4. `TYPE_STRING = 4` followed by _2 byte_ (u16) length of the string in bytes and _n byte_ string value (utf8 encoded string)

### statsd

The same as the influx, the `statsd` codec translates a single `statsd` measurement into a structured format. The structure is as follows:

```text
sam:7|c|@0.1
```

Translates to:

```json
{
  "type": "c",
  "metric": "sam",
  "value": 7,
  "sample_rate": 0.1
}
```

The following types are supported:

- `c` for `counter`
- `ms` for `timing`
- `g` for `gauge`
- `h` for `histogram`
- `s` for `sets`

For **gauge** there is also the field `action` which might be `add` if the value was prefixed with a `+`, or `sub` if the value was prefixed with a `-`

### yaml

En- and decodes [YAML](https://yaml.org).

### syslog

En- and decodes syslog messages (both, the standard IETF format and the old BSD format).
A syslog message following BSD format as follows:              

```text
<13>Jan  5 15:33:03 74794bfb6795 root[8539]: i am foobar
```

get translates to:

```json
{
  "severity": "notice",
  "facility": "user",
  "hostname": "74794bfb6795",
  "appname": "root",
  "msg": "i am foobar",
  "procid": 8539,
  "msgid": null,
  "protocol": "RFC3164",
  "protocol_version": null,
  "structured_data": null,
  "timestamp": 1609860783000000000
}
```

Syslog message following IETF standard as follows:

```text
<165>1 2021-03-18T20:30:00.123Z mymachine.example.com evntslog - ID47 [exampleSDID@32473 iut=\"3\" eventSource=\"Application\" eventID=\"1011\"] BOMAn application event log entry..."
```

get translates to:

```json
{
  "severity": "notice",
  "facility": "local4",
  "hostname": "mymachine.example.com",
  "appname": "evntsog",
  "msg": "BOMAn application event log entry...",
  "procid": null,
  "msgid": "ID47",
  "protocol": "RFC5424",
  "protocol_version": 1,
  "structured_data": {
              "exampleSDID@32473" :
              [
                {"iut": "3"},
                {"eventSource": "Application"},
                {"eventID": "1011"}
              ]
            },
  "timestamp": 1616099400123000000
}
```

!!! note
    invalid syslog message is treated under `3164` protocol and entire string goes to the `msg` of result object.
