# Safety Stack — Generic Templates for Cloud Cell Dispatch

Per `feedback_cloud_safety_features_required.md` (permanent memory rule),
EVERY cloud cell dispatch must include all four safety features:

1. **SSH-disconnect-aware launcher** — reattach via `sky logs` instead of teardown-then-retry
2. **Single-shot kill switch** — locks to first acquired cluster; prevents auto-restart on cluster death
3. **Periodic progress rsync** — 5-min incremental shard pull during run
4. **Independent watchdog** — 30-s state log via Lambda API direct (no SSH dependency)

This directory holds the GENERIC parameterized versions. Each new cell only needs:
- a per-cell config file (`cellN_config.sh`)
- a YAML
- a build script

Then dispatch with: `bash safety/safety_launch_all.sh cellN_config.sh`.

---

## Files

### Generic safety scripts (this directory)

- **`generic_smart_launch.sh`** — the launcher. Reattach on SSH-drop; preflight gate; sky api stop; PID lock; TRAP cleanup. Default `MAX_ACQUIRE_ATTEMPTS=1` (single-shot — never auto-restart on cluster death).
- **`generic_kill_switch.sh`** — locks to first cluster name from launcher log; kills launcher + tears down any 2nd cluster that slips through. Exits on success signal too.
- **`generic_progress_rsync.sh`** — every 5 min, rsync `REMOTE_OUTPUT_PATH` to `LOCAL_RESULTS_DIR`. `--partial` so interrupted transfers resume. Exits after 5 consecutive failures (cluster likely dead).
- **`generic_watchdog.sh`** — every 30 s, logs Lambda API instance state, sky status, launcher PID, SSH drop count, cum cost. Writes JSON state file. Curl uses User-Agent override to bypass Cloudflare WAF.
- **`safety_launch_all.sh`** — ORCHESTRATOR. Fires `generic_kill_switch`, `generic_watchdog`, `generic_progress_rsync` in background, then runs `generic_smart_launch` in foreground. TRAP cleans up bg workers on exit.

### Per-cell config + YAML + build (separate directories)

- `skypilot/cell3/{cell3_config.sh, cell3_distillation_h100.yaml, build_cell3_ship.sh}`
- `skypilot/cell4/{cell4_config.sh, cell4_hp12_v2_h100.yaml, build_cell4_ship.sh}`

---

## To dispatch a cell

```bash
# 1. Build the bundle (copies script + data + YAML to /root/cell?-ship/)
bash skypilot/cell3/build_cell3_ship.sh

# 2. Fire all 4 safety processes + launcher
nohup bash skypilot/safety/safety_launch_all.sh \
    skypilot/cell3/cell3_config.sh \
    > /mnt/d/AI/hd-instrument/data/cell3_orchestrator.log 2>&1 &

# 3. Watch
tail -F /mnt/d/AI/hd-instrument/data/cell3_smart_launch.log
tail -F /mnt/d/AI/hd-instrument/data/cell3_watchdog.log
cat /mnt/d/AI/hd-instrument/data/cell3_state.json
```

---

## Required config vars (cellN_config.sh)

```bash
CELL_NAME="CELL-3"
CLUSTER_PREFIX="cell3fd"
YAML_PATH="/root/cell3-ship/skypilot/cell3_distillation_h100.yaml"
BUNDLE_PATH="/root/cell3-ship"
EXPECTED_SCRIPT="exp_substrate_cell3_distilled_22M_student_v1.py"

SKUS_PRIORITY="gpu_1x_gh200 gpu_1x_h100_sxm5 gpu_1x_h100_pcie"
SKYPILOT_KNOWN_REGIONS="..."   # 18-region SkyPilot Lambda set

GPU_SPEC="H100:1"              # or "GH200:1"; YAML's any_of handles SKU fallback
AUTOSTOP_MIN=30
MAX_ACQUIRE_ATTEMPTS=1          # SAFETY default; never auto-restart

HF_TOKEN_FILE="/mnt/d/AI/hd-instrument/.hf_token"

# CRITICAL: SINGLE-QUOTE so ~ expands on REMOTE side (under ubuntu user)
REMOTE_OUTPUT_PATH='~/sky_workdir/data/exp_<anchor>/'
LOCAL_RESULTS_DIR="/mnt/d/AI/hd-instrument/data/cellN_results"

LAUNCHER_LOG="/mnt/d/AI/hd-instrument/data/cellN_smart_launch.log"
KILL_SWITCH_LOG="/mnt/d/AI/hd-instrument/data/cellN_kill_switch.log"
PROGRESS_RSYNC_LOG="/mnt/d/AI/hd-instrument/data/cellN_progress_rsync.log"
WATCHDOG_LOG="/mnt/d/AI/hd-instrument/data/cellN_watchdog.log"
WATCHDOG_STATE_JSON="/mnt/d/AI/hd-instrument/data/cellN_state.json"

LAUNCHER_LOCK_PATH="/tmp/${CLUSTER_PREFIX}_smart_launch.pid"
HOURLY_RATE_USD=4.29           # mid-estimate for watchdog cost display
```

---

## Hardening lessons baked in (do not regress)

- **SSH disconnect ≠ launch failure**: sky launch exits 255 when its streaming SSH drops, but cluster keeps running. Reattach via `sky logs` instead of teardown.
- **Single-shot default**: today's CELL-2 v3 burned $4.40 on retry-from-scratch loops. Never let a launcher auto-restart on cluster death unless explicitly authorized.
- **Single-quote `~/path` in shell vars**: bash expands `~` at assignment time using the LOCAL user's home. We want REMOTE expansion (ubuntu's home), so single-quote.
- **Cloudflare WAF blocks default urllib User-Agent**: Lambda API curl needs `-H "User-Agent: curl/7.81.0"`.
- **`pad_sequence` only right-pads**: write custom collators for LEFT-padding (cycle 142).
- **HF Datasets streaming auto-shards across DataLoader workers**: don't add a manual `idx % num_workers` filter (causes 1/64 over-sharding bug).
- **Preflight gate before any sky launch**: YAML script-reference consistency + bundle contents + orphan procs + Lambda API direct probe + sky status + HF token.

See `feedback_cloud_safety_features_required.md` in memory for the full rule.
