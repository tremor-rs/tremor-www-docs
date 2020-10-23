#!/bin/bash
# simple script to simulate a log stream

INPUT_FILE="data/logs_sample"
LOG_INTERVAL=0.01 # in seconds

# keep looping through the input file forever
while true; do
  while read log_line; do
    [ -z "$log_line" ] && continue # skip empty lines
    echo "$log_line"
    #echo "Sleeping for ${LOG_INTERVAL}s..." >&2
    sleep "$LOG_INTERVAL"
  done < "$INPUT_FILE"
done
