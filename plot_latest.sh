#!/bin/bash
set -e
while test $# -gt 1; do
    if [ "$1" = "--png" ]; then
        use_png=true
        shift
        output_file=$1
        shift
    else
        echo "Received invalid argument: $1. Usage: $0 [--png output_file]"
        exit 1
    fi
done

latest=$(find /tmp/profile/graphic/pipeline* -printf '%T+ %p\n' | sort -r | head -n 1 | awk '{ print $NF }')
if [ ${use_png} ]; then
    dot ${latest}  -T png -o ${output_file}
else
    dot ${latest}  -T x11 &
fi