#!/bin/bash
set -e
echo "=== bash-syntax check on updated files ==="
bash -n /mnt/d/AI/hd-instrument/skypilot/safety/generic_smart_launch.sh && echo "  generic_smart_launch.sh: OK"
bash -n /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_config.sh && echo "  cell3_config.sh: OK"
bash -n /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_smoke_config.sh && echo "  cell3_smoke_config.sh: OK"
bash -n /mnt/d/AI/hd-instrument/skypilot/cell4/cell4_config.sh && echo "  cell4_config.sh: OK"

echo ""
echo "=== source-check configs ==="
( source /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_smoke_config.sh && \
  echo "  smoke: CELL_NAME=$CELL_NAME CLUSTER_PREFIX=$CLUSTER_PREFIX EXTRA_SKY_ENVS_STR=$EXTRA_SKY_ENVS_STR" )
( source /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_config.sh && \
  echo "  full:  CELL_NAME=$CELL_NAME CLUSTER_PREFIX=$CLUSTER_PREFIX EXTRA_SKY_ENVS_STR=${EXTRA_SKY_ENVS_STR:-<unset>}" )
( source /mnt/d/AI/hd-instrument/skypilot/cell4/cell4_config.sh && \
  echo "  cell4: CELL_NAME=$CELL_NAME CLUSTER_PREFIX=$CLUSTER_PREFIX" )

echo ""
echo "=== STEP 1: CELL-3 build (~3 min for 21 GB copy) ==="
chmod +x /mnt/d/AI/hd-instrument/skypilot/safety/*.sh \
         /mnt/d/AI/hd-instrument/skypilot/cell3/*.sh \
         /mnt/d/AI/hd-instrument/skypilot/cell4/*.sh
date -u '+%H:%M:%S start cell3 build'
bash /mnt/d/AI/hd-instrument/skypilot/cell3/build_cell3_ship.sh 2>&1 | tail -15
date -u '+%H:%M:%S end cell3 build'

echo ""
echo "=== STEP 2: CELL-4 build (small, ~30 sec for 600 MB) ==="
date -u '+%H:%M:%S start cell4 build'
bash /mnt/d/AI/hd-instrument/skypilot/cell4/build_cell4_ship.sh 2>&1 | tail -15
date -u '+%H:%M:%S end cell4 build'

echo ""
echo "=== both builds DONE; ready to dispatch ==="
echo "/root/cell3-ship/ contents:"
du -sh /root/cell3-ship/ 2>&1
ls /root/cell3-ship/data/cell2_results/ | wc -l
echo "/root/cell4-ship/ contents:"
du -sh /root/cell4-ship/ 2>&1
ls /root/cell4-ship/data/cell2_results/ | wc -l
