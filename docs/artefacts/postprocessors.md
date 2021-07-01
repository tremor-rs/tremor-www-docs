# Postprocessors

Postprocessors operate on the raw data stream and transform it. They are run after data reaches the codec and do not know or care about tremor's internal representation.

Online codecs and postprocessors can be chained to perform multiple operations in succession.

## Supported Postprocessors

### lines

Delimits the output (events) into lines (by '\n').

### base64

Encodes raw data into base64 encoded bytes.

### length-prefixed

Prefixes the data with a network byte order (big endian) length of the data in bytes.

### gelf-chunking

Splits the data using [GELF chunking protocol](https://docs.graylog.org/en/3.0/pages/gelf.html#chunking).

### compression

Compresses event data.

Unlike decompression processors, the compression algorithm must be selected. The following compression post-processors are supported. Each format can be configured as a postprocessor.

Supported formats:

- gzip - GZip compression
- zlib - ZLib compression
- xz - Xz2 level 9 compression
- snappy - Snappy compression
- lz4 - Lz level 4 compression
- zstd - Zstd level 3 compression

### textual-length-prefix

Prefixes the data with the length of data given in ascii digits and a whitespace as used in [RFC 5425](https://tools.ietf.org/html/rfc5425#section-4.3) for TLS/TCP transport for syslog.
 