#!/bin/bash
config_file=./scripts/cronos-devnet.yaml
base_port=2600
data=./cronos_data

rm -rf $data
mkdir -p $data

pystarport init \
    --config $config_file \
    --data $data \
    --base_port $base_port \
    --no_remove
echo "pystarport start --data $data --quiet"
