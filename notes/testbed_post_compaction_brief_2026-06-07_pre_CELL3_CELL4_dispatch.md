# Testbed POST-COMPACTION BRIEF — pre-CELL-3+CELL-4 dispatch

**Compiled:** 2026-06-07 ~08:30 UTC
**Read this FIRST after any compaction event during this work-cycle.**

---

## 🔴 STATE: Building 4-layer safety stack templates BEFORE dispatching CELL-3 + CELL-4 to cloud

User explicit direction (today, in order):
1. CELL-2 v3 ran to completion at $26.58 (5.84M Wikipedia articles, 21 GB cache; left-padded)
2. CELL-3 + CELL-4 scripts built + hardened (commits 3e05651, fd657de, 19abda1)
3. Audit-of-audit + Wikipedia text hardening complete
4. User chose **Path B** for safety stack: build GENERIC parameterized templates first
5. User explicit: **BOTH CELL-3 + CELL-4 go to cloud** (not local)
6. User direction: **prepare for compaction BEFORE launch**

---

## What's DONE for CELL-3 + CELL-4

### CELL-3 script: `experiments/exp_substrate_cell3_distilled_22M_student_v1.py`
- 22M sentence-transformer-style student: 6 layers, hidden=384, embed=128, vocab=128K
- Train from BASE (Q4 HF lock)
- Feature-mimic MSE on CELL-2 v3 cache (Research Q-CELL-3-1)
- Self-test PASS (28.3M params; in 18-30M PROT-022 budget)
- Speedups: pre-tokenize parallel + batch=256 + LR=6e-4 + workers=16 + prefetch=4 + persistent + torch.compile opt-in + stub filter + best-only ckpt + MAX_TOK=512 (matches CELL-2 v3) + TF32-high
- Audit-of-audit hardening: None-text guard, per-text exception fallback, numpy-pack pretokenize (no Python int memory bomb), Wikipedia text hazards smoke-tested

### CELL-4 script: `experiments/exp_substrate_hp12_v2_100k_pseudoinverse_v1.py`
- 100K facts, pseudoinverse write rule (cycle 143 LOCK)
- PCA whitening (cycle 136+140), LEFT-padding (cycle 142)
- HNSW ef_search=256 informational; exhaustive in-fragment (~819 keys)
- N=2048 × 128 fragments (Research Q-CELL-4-1)
- Per-fragment cap = alpha_c × dim = 819 (was bug: used dim)
- **Multi-head H=2 BFT** (Research F4 spec): random orthogonal rotations per head; per-head pseudoinverse; read-time average. Saturation regime selftest PASS.
- `--noise-sweep` flag for capacity profile

### Both scripts: self-tests PASS, hardened, committed and pushed

---

## What's IN PROGRESS: Generic 4-layer safety stack at `skypilot/safety/`

### Built so far (✓):
- `safety/generic_smart_launch.sh` — SSH-disconnect-aware reattach via sky logs; MAX_ACQUIRE_ATTEMPTS=1 default (single-shot safety); PID lock + TRAP cleanup + preflight gate + sky api stop
- `safety/generic_kill_switch.sh` — locks to first cluster; kills launcher + tears down 2nd cluster
- `safety/generic_progress_rsync.sh` — 5-min cluster output pull; --partial; single-quote ~ for remote expansion (CELL-2 v3 bug fix)
- `safety/generic_watchdog.sh` — 30-s state log; Lambda API direct probe (uses User-Agent for Cloudflare bypass); cum cost; SSH-drop count
- `safety/safety_launch_all.sh` — ORCHESTRATOR; sources config + fires all 4 + TRAP-cleanup

### Still NEEDED (in priority order):
1. `safety/README.md` — how to add a new cell config
2. **`cell3/cell3_config.sh`** — exports vars for CELL-3 (CRITICAL; cell-specific)
3. **`cell3/cell3_distillation_h100.yaml`** — copy from cell5 YAML pattern; cu121 (x86 H100); add Wikipedia pre-download (CELL-3 needs raw text)
4. **`cell3/build_cell3_ship.sh`** — copy from build_cell2_ship.sh pattern; bundles script + Wikipedia data
5. **`cell4/cell4_config.sh`** — exports vars for CELL-4
6. **`cell4/cell4_hp12_v2_h100.yaml`** — H100 or GH200 (cu121 or cu128 picked by SKU); script + cell2 cache rsync to cluster
7. **`cell4/build_cell4_ship.sh`** — bundle script + cell2 cache shards

### NOT YET BUILT but on the path:
8. Test of generic safety stack with a dry-run (DRY_RUN flag to skip actual sky launch)
9. Dispatch CELL-3 + CELL-4 via `bash safety/safety_launch_all.sh cell3/cell3_config.sh` (similar for cell4)

---

## Required config vars per cell (from generic_*.sh source)

```bash
# Identity
CELL_NAME="CELL-3"                    # display name
CLUSTER_PREFIX="cell3fd"              # cluster name prefix (cell3fd-HHMMSS)

# Paths
YAML_PATH="/root/cell3-ship/skypilot/cell3_distillation_h100.yaml"
BUNDLE_PATH="/root/cell3-ship"
EXPECTED_SCRIPT="exp_substrate_cell3_distilled_22M_student_v1.py"

# Capacity polling
SKUS_PRIORITY="gpu_1x_gh200 gpu_1x_h100_sxm5 gpu_1x_h100_pcie"
SKYPILOT_KNOWN_REGIONS="us-east-1 us-east-2 us-east-3 us-west-1 us-west-2 us-west-3 us-south-1 us-south-2 us-south-3 us-midwest-1 us-southeast-1 asia-northeast-1 asia-northeast-2 asia-south-1 australia-east-1 europe-central-1 europe-south-1 me-west-1"

# Cloud-launch params
GPU_SPEC="H100:1"                     # or GH200:1
AUTOSTOP_MIN=30
HF_TOKEN_FILE="/mnt/d/AI/hd-instrument/.hf_token"
MAX_ACQUIRE_ATTEMPTS=1                # SAFETY: never auto-restart on cluster death

# Output paths
REMOTE_OUTPUT_PATH='~/sky_workdir/data/exp_substrate_cell3_distilled_22M_student_v1/'  # SINGLE-QUOTED so ~ expands on REMOTE side
LOCAL_RESULTS_DIR="/mnt/d/AI/hd-instrument/data/cell3_results"

# Log paths
LAUNCHER_LOG="/mnt/d/AI/hd-instrument/data/cell3_smart_launch.log"
KILL_SWITCH_LOG="/mnt/d/AI/hd-instrument/data/cell3_kill_switch.log"
PROGRESS_RSYNC_LOG="/mnt/d/AI/hd-instrument/data/cell3_progress_rsync.log"
WATCHDOG_LOG="/mnt/d/AI/hd-instrument/data/cell3_watchdog.log"
WATCHDOG_STATE_JSON="/mnt/d/AI/hd-instrument/data/cell3_state.json"

# State + cost
LAUNCHER_LOCK_PATH="/tmp/cell3fd_smart_launch.pid"
HOURLY_RATE_USD=4.29                  # H100 SXM5; adjust per actual SKU acquired

# Optional pre-launch hook (e.g., upload cell2 cache to BUNDLE_PATH)
pre_launch_hook() {
    # ... cell-specific setup
    return 0
}
```

---

## Dispatch sequence ONCE everything is built

```bash
# Step 1: build the cell's bundle
bash skypilot/cell3/build_cell3_ship.sh

# Step 2: dispatch (orchestrator fires all 4 safety procs + launcher)
nohup bash skypilot/safety/safety_launch_all.sh skypilot/cell3/cell3_config.sh \
    > data/cell3_orchestrator.log 2>&1 &
```

Same pattern for CELL-4.

---

## Cost estimates (with all speedups applied)

| Cell | Scope | Wall | Cost (GH200) | Cost (H100 SXM5) |
|---|---|---|---|---|
| CELL-3 | 1M smoke | ~5-8 min | $0.30 | $0.55 |
| CELL-3 | full 5.84M | ~20-30 min | $1.00-1.20 | $2.00 |
| CELL-4 | 100K facts H=2 | ~15-25 min | $0.40-0.60 | $0.75-1.00 |

**User has not yet decided CELL-3 scope** (1M smoke first vs full 5.84M). My recommendation was smoke-first.

---

## All today's commits to recall

```
19abda1  testbed: harden CELL-3 against Wikipedia text hazards + audit-of-audit fixes
3e05651  testbed: audit CELL-3 + CELL-4 vs full bug catalog + add Research H=2 multi-head
fd657de  testbed: CELL-3 speedups (A+B+D+F+G+H) -- 20-30x wall reduction estimated  (had research's SRHT in same commit due to autonomous Research session timing)
df0ab71  testbed: progress_rsync -- pull shards from cluster every 5 min during run
da12141  testbed: kill switch -- if current cell2wiki cluster dies, do NOT auto-restart
3dbea95  testbed: HARDEN smart launchers against SSH disconnects + CELL-3 script
27ddcdd  testbed: comprehensive watchdog for CELL-2 dispatch + Lambda API helper
bbf731e  testbed: CELL-2 v3 COMPLETE -- 5.84M Wikipedia articles, LEFT-padded cache
```

---

## Today's full cost ledger (as of 08:30 UTC)

| Item | Cost | Notes |
|---|---|---|
| Earlier (CLOUD-1, CELL-1, 70B-Instruct, sunk) | $3.97 | morning |
| CELL-2 v2 (UNIFORM 800K right-pad) | $2.24 | accepted then re-extracted |
| CELL-2 v3 attempts 1-3 sunk (SSH-drop bug, pre-hardening) | $4.40 | |
| CELL-2 v3 attempt 4 (the successful run, hardened launcher) | $22.18 | full 5.84M |
| CELL-5 cascade distillation FD | $2.67 | HARD_PASS ratio 3.91 |
| HNSW EF calibration (WSL local) | $0 | |
| Q4 LoRA retrieval test (local 4060 Ti) | $0 | |
| **TODAY TOTAL** | **$35.46** | |
| **Projected through CELL-3 + CELL-4** | **$37-39** (CELL-3 1M smoke + CELL-4 cloud) | |
| **Drill Y envelope** | $100-200 | 60-80% under budget |

---

## SAFETY STACK STATUS (the user's permanent rule)

Per `feedback_cloud_safety_features_required.md` (saved as memory; permanent):
- Hardened launcher (SSH-disconnect-aware reattach) ✓ generic version built
- Single-shot kill switch (no auto-restart) ✓ generic version built
- 5-min progress rsync ✓ generic version built
- 30-s watchdog (independent of SSH) ✓ generic version built
- Orchestrator (`safety_launch_all.sh`) ✓ built
- Per-cell config (cell3_config.sh, cell4_config.sh) ❌ NOT YET built
- Per-cell YAML + build script ❌ NOT YET built

**NEXT IMMEDIATE STEPS on resume:**
1. Write `skypilot/safety/README.md`
2. Build `skypilot/cell3/{cell3_config.sh, cell3_distillation_h100.yaml, build_cell3_ship.sh}`
3. Build `skypilot/cell4/{cell4_config.sh, cell4_hp12_v2_h100.yaml, build_cell4_ship.sh}`
4. **Test the generic safety stack with a dry-run** (mock cluster, real generic scripts) before any actual cloud spend
5. Ask user CELL-3 scope (1M smoke vs full 5.84M) — still pending
6. Dispatch CELL-3 + CELL-4

---

## What Research delivered today (relevant to our work)

- **CELL-3 spec finalized**: feature-mimic MSE on CELL-2 cache; 22M student; train from BASE (Q4 HF)
- **CELL-4 spec finalized**: N=2048 × 128 fragments + pseudoinverse + PCA + LEFT-pad + ef=256 + M_max>=300 + **H=2 multi-head BFT** (added 2026-06-07 ~07:00 UTC)
- CELL-2 v3 800K v2 cache representativeness UNIFORM confirmed; ACCEPT decision
- 70B-Instruct ARCHITECTURE_ROBUST + Instruct-destroys-mid-depth lock
- Cycle 142 left-padding LOCKED (+22.6% Q4 empirical)
- Cycle 143 PINV + whitening LOCKED universal recipe
- Production architecture: PRODUCTION_ARCHITECTURE_LOCKED_2026-06-07.md

---

## END BRIEF

This brief is referenced by `MEMORY.md` for post-compaction discoverability.

If compaction hits between now and CELL-3+CELL-4 dispatch, resume here. Pick up at "NEXT IMMEDIATE STEPS on resume" above.
