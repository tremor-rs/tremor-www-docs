# Preprocessors

Preprocessors operate on the raw data stream and transform it. They are run before data reaches the codec and do not know or care about tremor's internal representation.

Online codecs, preprocessors can be chained to perform multiple operations in succession.

## Supported Preprocessors

### lines

Splits the input into lines, using character 10 `\n` as the line separator.

Buffers any line fragment that may be present (after the last line separator), till more data arrives. This makes it ideal for use with streaming onramps like [tcp](onramps.md#tcp), to break down incoming data into distinct events.

Any empty lines present are forwarded as is -- if you want to remove them, please chain the [remove-empty](#remove-empty) preprocessor with this preprocessor. An example:

```yaml
preprocessors:
  - lines
  - remove-empty
```

Note: the proliferation of various lines preprocessors here will go away once preprocessors [support configuration](https://github.com/tremor-rs/tremor-rfcs/pull/31).

### lines-null

Variant of the [lines](#lines) preprocessor, that uses null byte `\0` as the line separator.

### lines-pipe

Variant of the [lines](#lines) preprocessor, that uses pipe character `|` as the line separator.

### lines-no-buffer

Variant of the [lines](#lines) preprocessor, that does *not* buffer any data that may be present after the last line separator -- the fragment is forwarded as is (i.e. treated as a full event).

### lines-cr-no-buffer

Variant of the [lines-no-buffer](#lines-no-buffer) preprocessor, that uses character 13 `\r` ([carriage return](https://en.wikipedia.org/wiki/Carriage_return#Computers)) as the line separator.

### base64

Decodes base64 encoded data to the raw bytes.

### decompress

Decompresses a data stream. It is assumed that each message reaching the decompressor is a complete compressed entity.

The compression algorithm is detected automatically from the supported formats. If it can't be detected, the assumption is that the data was decompressed and will be sent on. Errors then can be transparently handled in the codec.

Supported formats:

- gzip
- zlib
- xz
- snappy
- lz4

### gzip

Decompress GZ compressed payload.

### zlib

Decompress Zlib ( deflate ) compressed payload.

### xz

Decompress Xz2 ( 7z ) compressed payload.

### snappy

Decompress framed snappy compressed payload ( does not support raw snappy ).

### lz4

Decompress Lz4 compressed payload.

### gelf-chunking

Reassembles messages that were split apart using the [GELF chunking protocol](https://docs.graylog.org/en/3.0/pages/gelf.html#chunking).

If the GELF messages were sent compressed, you can decompress them by chaining the [decompress](#decompress) preprocessor. An example is documented [here](onramps.md#udp-onramp-example-for-gelf) -- you may need to apply `decompress` either before and/or after the reassembly here, depending on how your GELF client(s) behave.

### remove-empty

Removes empty messages (aka zero len).

### length-prefixed

Seperates a continous stream of data based on length prefixing. The length for each package in a stream is based on the first 64 bit decoded as an unsigned big endian value.
