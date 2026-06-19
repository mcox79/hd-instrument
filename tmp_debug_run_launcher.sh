#!/bin/bash
# Run the smart launcher manually with set -x trace; output to a file we can read
exec > /tmp/debug_launcher.log 2>&1
set -x
bash -x /mnt/d/AI/hd-instrument/skypilot/safety/generic_smart_launch.sh \
    /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_smoke_config.sh
