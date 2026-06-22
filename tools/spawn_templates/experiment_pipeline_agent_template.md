# Experiment Pipeline Agent Template

**Version:** 1.0 (2026-06-22, per USER autonomous arc directive)
**Author:** Research (Director / team lead)
**Purpose:** Reduce main-thread tie-up from 5+ sequential sync spawns per experiment to a
single background-mode spawn. This template is the parameterized prompt that a Director
main-thread spawn issues to a background `hdi_exp_dev`-flavored agent that handles the full
experiment lifecycle autonomously.

---

## When to Use This Template

Use when you have:
- A cell already identified by name (existing or to be authored from a base cell)
- Pre-reg bands and a corpus settled (or resolvable at spawn time)
- A clear queue target (remote_cpu_queue or overnight_queue)
- Ability to wait for a one-paragraph completion summary rather than mid-pipeline results

Do NOT use this template when:
- The cell needs a design SCHEMA-VET first (SCHEMA-VET is synchronous; pre-reg discipline
  requires cert-owner sign-off BEFORE dispatch)
- The cell involves concurrent Store writes from another pipeline agent (single-writer window)
- The cell is GPU-only with an unverified PROT-020 import-torch gate (see TODO #1)

---

## Parameters

The parent (Director main thread) fills every `{{PARAM}}` before issuing the spawn prompt.

| Parameter | Description | Example |
|---|---|---|
| `{{CELL_NAME}}` | Anchor name + file stem | `n4_kwta_soft_decode_v1` |
| `{{CELL_FILE}}` | Path relative to repo root | `experiments/exp_n4_kwta_soft_decode_v1.py` |
| `{{BASE_CELL}}` | Existing cell to fork (or "NONE — write from scratch") | `experiments/exp_n3_mkn_smoothing_v1.py` |
| `{{PRE_REG_BANDS}}` | HARD_PASS / MIDDLE_BAND / HARD_FAIL criteria, verbatim from pre-reg note | (paste bands here) |
| `{{PRE_REG_DIRECTION}}` | Required improvement direction (higher/lower/etc.) | "MKN substrate_bpc LOWER than JM anchor" |
| `{{CORPUS}}` | Corpus name + provenance requirement | `residuals_per_token.npz on marsh@home; allow_synthetic=False` |
| `{{V_C}}` | Concept codebook size | `1024` |
| `{{N_DIM}}` | Embedding dimension | `16384` |
| `{{K}}` | Context depth | `1` |
| `{{SEEDS}}` | Full-run seed list | `[7, 17, 23]` |
| `{{QUEUE_TARGET}}` | Which queue to dispatch to | `remote_cpu_queue` |
| `{{SMOKE_CONFIG}}` | Smoke config override (seeds, M, N_DIM) | `SEEDS=[1]; MAX_DOCS=200; N_DIM_SMOKE=512` |
| `{{FULL_CONFIG}}` | Full-run config summary | `SEEDS=[7,17,23]; MAX_DOCS=100000; N_DIM=16384` |
| `{{INSTRUMENTATION_REQS}}` | Required metrics.json fields beyond defaults | `per_unit per (seed, k_value); zero_llm_calls_at_inference; ceiling_bpc per arm` |
| `{{ESTIMATED_WALL_PER_SEED}}` | Measured (not quoted) per-seed wall estimate | `~15 min (empirical single-seed near-full-scale timing)` |
| `{{TIMEOUT_H}}` | Full-run timeout in hours (default 4) | `4` |
| `{{ATOM_ID_CANDIDATE}}` | Proposed Store atom qualified ID | `math::T3/EXP_n4_kwta_soft_decode_v1` |
| `{{PRE_REG_NOTES_PATH}}` | Path to pre-reg file already committed | `notes/n4_kwta_soft_decode_pre_reg_2026-06-22.md` |

---

## Spawn Prompt (parameterized)

Copy this block, substitute all `{{PARAM}}` values, and issue as the spawn prompt to the
background `hdi_exp_dev`-flavored agent. Do not modify the structural sections — they carry
load-bearing discipline instructions.

---

```
You are an hdi_exp_dev pipeline agent running the FULL experiment lifecycle for:

  CELL:          {{CELL_NAME}}
  FILE:          {{CELL_FILE}}
  BASE CELL:     {{BASE_CELL}}
  QUEUE:         {{QUEUE_TARGET}}
  TIMEOUT:       {{TIMEOUT_H}} hours for the full run

Your job is to run the pipeline end-to-end and return a SINGLE completion summary.
Do NOT schedule ScheduleWakeup. Do NOT file intermediate notes. Do NOT modify the Store.
Your only output artifact is ONE completion note (see Section 9) + ONE reply paragraph
(see Section 10).

---

## REPO CONTEXT

Repo root:     D:/AI/hd-instrument
Python:        D:/AI/hd-instrument/.venv/Scripts/python.exe  (NEVER system python)
CWD resets:    every Bash call — always cd /d/AI/hd-instrument before any command

---

## 0. STARTUP CHECKLIST (do first, before anything else)

a. Confirm the pre-reg note exists and is committed:
   git -C /d/AI/hd-instrument log --oneline --follow -- {{PRE_REG_NOTES_PATH}} | head -3
   If not committed: STOP. File a blocker note to Director. Do not proceed.

b. Confirm .venv is present:
   ls /d/AI/hd-instrument/.venv/Scripts/python.exe
   If absent: STOP.

c. Confirm corpus / data dependency exists on the target runner:
   For remote_cpu_queue: SSH check
     ssh -o ConnectTimeout=20 marsh@home 'python.exe -c "import pathlib; p=pathlib.Path(\"C:/dev/hd-instrument/data/...\"); print(p.exists())"'
   For local_cpu_queue: local ls check

d. Read fleet_waiting_on.md to confirm no single-writer Store window is open:
   cat /d/AI/hd-instrument/data/fleet_waiting_on.md | grep -A5 "## skunkworks"
   If skunkworks is mid-Store-write: wait until their section clears before atomizing.

---

## 1. PRE-FLIGHT: AST-CHECK + SELF-TEST

### 1a. Cell authorship (if CELL_FILE does not exist yet)

Fork {{BASE_CELL}} to {{CELL_FILE}}. Required baked-in patterns (every N-series cell):

  - `_LLM_CALL_COUNTER = [0]` at module top (Skunkworks structural blocker #3)
  - `zero-D-overlap fallback` in batched_token_logprob (Fix #6 pattern from
    exp_n4_kwta_soft_decode_v1.py / exp_n3_mkn_smoothing_v1.py)
  - per_unit entry per (seed, arm_config) stored in metrics.json (Skunkworks #1)
  - cv <= 0.05 computed across seeds in verdict() (Skunkworks #2)
  - VQ-floor / ceiling_bpc decomposition reported per arm (Skunkworks #4)
  - CONFIG_VERSION includes ALL BPC-affecting params; computed dynamically from actual
    config (not hardcoded label strings -- the "stale @M=10k label" lesson)
  - Per-seed checkpoint resume via experiments/_seed_checkpoint.py
  - ANCHOR_NAME = "{{CELL_NAME}}" at module scope (AST-verifiable constant)
  - `run_mode = "full"` default (PROT-021); smoke only via --smoke flag or
    HDLAB_RUN_MODE=smoke
  - Pre-reg direction check in verdict(): large abs-delta in WRONG direction = HARD_FAIL
    not MIDDLE_BAND (Skunkworks n3 SimVQ catch; Fix #5 sibling discipline)
  - allow_synthetic=False on any corpus loader (fail-loud; no silent bigram-Markov fallback)

### 1b. AST-verify module-level constants are real Assign nodes (not docstring text):

  cd /d/AI/hd-instrument && .venv/Scripts/python.exe -c "
  import ast
  t = ast.parse(open('{{CELL_FILE}}', encoding='utf-8').read())
  names = [n.id for node in t.body if isinstance(node, ast.Assign)
           for n in node.targets if isinstance(n, ast.Name)]
  required = ['ANCHOR_NAME', 'CONFIG_VERSION', '_LLM_CALL_COUNTER']
  missing = [r for r in required if r not in names]
  print('MISSING CONSTANTS:', missing if missing else 'NONE')
  "

  If any are missing: fix the cell before proceeding.

### 1c. REQUIRED_FIELDS check (metrics.json will have these):

  Verify cell code writes at minimum:
    anchor_name, run_mode, n_seeds, config_version, per_seed, verdict,
    verdict_msg, zero_llm_calls_at_inference

  Do a grep: grep -n "zero_llm_calls_at_inference\|per_seed\|config_version" {{CELL_FILE}}
  If missing: add them before smoke dispatch.

### 1d. Self-test:

  cd /d/AI/hd-instrument && timeout 150 .venv/Scripts/python.exe {{CELL_FILE}} --self-test 2>&1 | tail -20

  PASS = "selftest" / "PASS" / "OK" in output, no traceback.
  FAIL = stop; fix the cell.

### 1e. Per-seed runtime measurement (Fix #3 — MANDATORY before full dispatch):

  Run ONE seed at near-full scale (not smoke, not the full grid):

    cd /d/AI/hd-instrument && timeout 1800 .venv/Scripts/python.exe {{CELL_FILE}} \
      --smoke 2>&1 | tail -30

  Record the per-seed wall_s from the single-seed output. If the smoke wall > 10 min,
  escalate to Director with: "per-seed wall {{measured}}; full grid ETA {{extrapolated}};
  recommend queue {{queue_recommendation}}; proceed?" and WAIT for reply.

  For remote_cpu_queue cells: this near-full-scale timing is the SSH-equivalent:
    Run smoke locally, measure model-load + single-seed encoding overhead, extrapolate.

---

## 2. SMOKE-DISPATCH SEQUENCE

### 2a. Commit cell + pre-reg (verify-the-referent on the commit):

  cd /d/AI/hd-instrument
  # guard against shared-index race
  for i in 1 2 3; do [ ! -f .git/index.lock ] && break; sleep 2; done
  git add -- {{CELL_FILE}}
  git commit -m "exp: add {{CELL_NAME}} cell for smoke + full pipeline run" -- {{CELL_FILE}}

  Record the commit hash. This is the cell_commit for the cert_ledger_writer row.

### 2b. Dispatch smoke to {{QUEUE_TARGET}}:

  For remote_cpu_queue:
    bash tools/orchestrator/queue_add.sh remote_cpu_queue \
      {{CELL_NAME}}_smoke \
      {{CELL_FILE}} \
      {{PRE_REG_NOTES_PATH}} \
      3600 \
      -- \
      HDLAB_RUN_MODE=smoke {{SMOKE_CONFIG_ENV_OVERRIDES}}

  For local_cpu_queue:
    bash tools/orchestrator/queue_add.sh local_cpu_queue \
      {{CELL_NAME}}_smoke \
      {{CELL_FILE}} \
      {{PRE_REG_NOTES_PATH}} \
      3600 \
      -- \
      HDLAB_RUN_MODE=smoke {{SMOKE_CONFIG_ENV_OVERRIDES}}

  Note: push to origin/main is required for remote_cpu_queue before dispatch
  (remote runner reads origin/main). Verify:
    git push origin main
    # if push is harness-DENIED to this role: route to Orchestrator with the commit hash
    # and ask Orchestrator to push + dispatch. Then WAIT for Orchestrator confirmation
    # before entering the smoke-poll loop.

### 2c. Post-dispatch verify-it-starts (within first 5 min):

  SMOKE_STATUS_CHECK:
    For remote_cpu_queue:
      ssh -o ConnectTimeout=20 marsh@home \
        'python.exe -c "import json,pathlib; q=json.load(open(\"C:/dev/hd-instrument/data/remote_cpu_queue/queue.json\")); e=[x for x in q[\"experiments\"] if \"{{CELL_NAME}}_smoke\" in x[\"name\"]]; print({k:e[0].get(k) for k in (\"status\",\"started_at\",\"claimed_by\")} if e else \"NOT_FOUND\")" 2>&1 | tr -d "\r"'

    Expected within 2 min: status=running or status=pending (not NOT_FOUND).
    If NOT_FOUND after 5 min: re-check queue file spelling; re-dispatch with --allow-duplicate.
    If status=failed after <60s: the cell has an import/NameError — pull metrics.json + diagnose.

---

## 3. SMOKE-POLL LOOP (in-spawn polling; no background bash watcher — Fix #4)

Poll every 60 seconds. Emit one-line status update per poll.

```python
# Pseudocode for the polling logic (adapt to actual SSH/local check):
import time
MAX_SMOKE_WAIT = 60 * 20  # 20 min; smoke should complete in <5 min
POLL_INTERVAL = 60
elapsed = 0
while elapsed < MAX_SMOKE_WAIT:
    status = pull_queue_status("{{CELL_NAME}}_smoke")
    if status in ("completed", "failed"):
        break
    print(f"  [{elapsed//60}min] smoke still running; status={status}")
    time.sleep(POLL_INTERVAL)
    elapsed += POLL_INTERVAL
if elapsed >= MAX_SMOKE_WAIT:
    STOP: "smoke timed out after 20min — diagnose runner liveness before proceeding"
```

Bash equivalent (run as a tight Bash loop with sleep 60):
  For remote_cpu_queue:
    for i in $(seq 1 20); do
      OUT=$(ssh -o ConnectTimeout=20 marsh@home \
        'python.exe -c "import json,pathlib; q=json.load(open(\"C:/dev/hd-instrument/data/remote_cpu_queue/queue.json\")); e=[x for x in q[\"experiments\"] if \"{{CELL_NAME}}_smoke\" in x[\"name\"]]; s=e[0].get(\"status\",\"?\") if e else \"NOT_FOUND\"; print(s)"' 2>/dev/null | tr -d '\r')
      echo "[$(date -u +%H:%M:%S)] smoke poll $i: $OUT"
      echo "$OUT" | grep -qiE "completed|failed" && echo "SMOKE_DONE" && break
      sleep 60
    done

---

## 4. SMOKE-VET INLINE

On smoke completion, pull metrics.json and verify ALL of the following. Fail any single
check = fix cell + re-smoke before proceeding to full dispatch.

### Fix #5 — run_mode check FIRST:

  cd /d/AI/hd-instrument
  # For remote runner: scp or SSH-cat
  ssh -o ConnectTimeout=20 marsh@home \
    'python.exe -c "import json,pathlib; m=json.load(open(\"C:/dev/hd-instrument/data/exp_{{CELL_NAME}}_smoke/metrics.json\")); print(\"run_mode:\",m.get(\"run_mode\"),\"verdict:\",m.get(\"verdict\"))"' \
    2>/dev/null | tr -d '\r'

  REQUIRED: run_mode == "smoke" (verifies cell honors HDLAB_RUN_MODE).
  If run_mode == "full": the cell's run-mode detection is broken — fix before proceeding.

### Smoke-VET checklist:

  a. `run_mode` == "smoke" (Fix #5 gate — already done above)
  b. `n_seeds` matches smoke config (expected: 1 or as configured in {{SMOKE_CONFIG}})
  c. `per_seed` is a non-empty list with at least one entry per (seed, arm_config)
  d. `zero_llm_calls_at_inference` == True (or 0) in metrics — substrate-only gate logged
  e. `ceiling_bpc` (or VQ-floor equivalent) is present per arm
  f. `cv` is finite (not NaN) — even on 1 smoke seed, the computation must not crash
  g. verdict + verdict_msg present (doesn't matter if smoke is HARD_FAIL — we test harness)
  h. No NaN in any per_seed entry's numeric fields
  i. No traceback in the cell output (pull /tmp/<task_id>.output or SSH equivalent)
  j. Anchor_name in metrics matches "{{CELL_NAME}}"

  Re-derive at least one cited number from per_seed:
    python -c "
    import json
    m = json.load(open('data/exp_{{CELL_NAME}}_smoke/metrics.json'))
    pu = m.get('per_seed', [])
    print('per_seed count:', len(pu))
    if pu:
        bpcs = [e.get('substrate_bpc', e.get('bpc')) for e in pu if 'substrate_bpc' in e or 'bpc' in e]
        print('sample substrate_bpc values:', bpcs[:5])
        print('verdict_msg snippet:', m.get('verdict_msg','')[:200])
    "
    Confirm: the per_seed data is self-consistent and the verdict_msg numbers are
    derivable from per_seed (not phantoms).

  SMOKE GREEN = all 10 checks pass + re-derived number consistent.
  SMOKE RED = any check fails. Fix, re-commit, re-smoke. Do NOT proceed to full dispatch.

---

## 5. FULL-DISPATCH SEQUENCE (conditional on smoke green)

### 5a. Commit smoke metrics (path-scoped; verify no index.lock):

  cd /d/AI/hd-instrument
  for i in 1 2 3; do [ ! -f .git/index.lock ] && break; sleep 2; done
  git add -- data/exp_{{CELL_NAME}}_smoke/metrics.json
  git commit -m "exp: smoke metrics for {{CELL_NAME}} — harness OK" \
    -- data/exp_{{CELL_NAME}}_smoke/metrics.json

### 5b. Dispatch full:

  bash tools/orchestrator/queue_add.sh {{QUEUE_TARGET}} \
    {{CELL_NAME}} \
    {{CELL_FILE}} \
    {{PRE_REG_NOTES_PATH}} \
    $(({{TIMEOUT_H}} * 3600))

  For remote_cpu_queue: push to origin/main BEFORE dispatch (remote reads origin/main).
  Push is harness-DENIED to exp_dev flavor: route to Orchestrator or Director main thread
  with: "ready to dispatch {{CELL_NAME}} full; commit is <hash>; please push + dispatch."
  Then WAIT for confirmation.

### 5c. Post-dispatch verify-it-starts:

  Same pattern as smoke (Section 2c) but for the full job name.
  Check within 5 min; confirm status=running + first partial appears within:
    - CPU queue: within 10 min (past model-load)
    - GPU queue: within 5 min (GPU load is fast)
  If no first partial after 20 min on CPU (30 min on GPU): escalate to Orchestrator.

  Emit Fix #7 status line:
    "Standing by for full run. ETA ~{{ESTIMATED_WALL_PER_SEED}} x {{len(SEEDS)}} seeds.
     Next check in 30 min. You can interrupt anytime."

---

## 6. FULL-RUN POLL LOOP (in-spawn; no background bash — Fix #4)

Poll every 5 minutes. Emit a one-line status update every 30 min (Fix #7).
Hard timeout: {{TIMEOUT_H}} hours from dispatch.

```python
# Pseudocode (adapt to Bash or Python as convenient)
MAX_WAIT_S = {{TIMEOUT_H}} * 3600
POLL_INTERVAL = 300   # 5 min
STATUS_INTERVAL = 1800  # 30 min — Fix #7 status-line cadence
elapsed = 0
last_status_print = 0
while elapsed < MAX_WAIT_S:
    status, wall_s, n_partials = pull_full_status("{{CELL_NAME}}")
    if status in ("completed", "failed"):
        break
    if elapsed - last_status_print >= STATUS_INTERVAL:
        print(f"  [{elapsed//3600:.1f}h] full run: status={status}, "
              f"partials_so_far={n_partials}, wall_s={wall_s}")
        last_status_print = elapsed
    sleep(POLL_INTERVAL)
    elapsed += POLL_INTERVAL
if elapsed >= MAX_WAIT_S:
    STOP: "full run timed out after {{TIMEOUT_H}}h — escalate to Director"
```

Bash equivalent (run with run_in_background NOT recommended — use in-spawn tight loop):
  TIMEOUT_S=$(({{TIMEOUT_H}} * 3600))
  START=$(date +%s)
  LAST_PRINT=0
  for i in $(seq 1 $((TIMEOUT_S / 300))); do
    NOW=$(date +%s)
    ELAPSED=$((NOW - START))
    OUT=$(ssh -o ConnectTimeout=20 marsh@home \
      'python.exe -c "import json,pathlib; q=json.load(open(\"C:/dev/hd-instrument/data/{{QUEUE_TARGET}}/queue.json\")); e=[x for x in q[\"experiments\"] if x[\"name\"]==\"{{CELL_NAME}}\"]; s=e[0].get(\"status\",\"?\") if e else \"NOT_FOUND\"; w=e[0].get(\"wall_s\",\"?\") if e else \"?\"; print(s,w)"' \
      2>/dev/null | tr -d '\r')
    echo "$OUT" | grep -qiE "completed|failed" && echo "FULL_DONE: $OUT" && break
    SINCE_PRINT=$((ELAPSED - LAST_PRINT))
    if [ $SINCE_PRINT -ge 1800 ]; then
      echo "[$(date -u +%H:%M:%S)] full poll $i: $OUT (elapsed ${ELAPSED}s)"
      LAST_PRINT=$ELAPSED
    fi
    sleep 300
  done

---

## 7. FULL-VET INLINE

Pull and verify metrics.json for the FULL run. This is the cert-candidate verdict.

### Fix #5 — run_mode FIRST:

  Verify `run_mode == "full"` BEFORE drawing any cert-grade conclusion.
  If run_mode == "smoke": something went wrong with the dispatch (wrong env var or cell
  re-used smoke flag). Do NOT vet as cert-grade. Diagnose + re-dispatch.

### Full-VET checklist (minimum; Skunkworks will do the independent off-data recompute):

  a. `run_mode` == "full" (Fix #5 gate)
  b. `n_seeds` matches {{SEEDS}} (e.g., 3 for seeds=[7,17,23])
  c. `per_seed` has N_seeds × N_arm_configs entries (full grid coverage)
  d. `zero_llm_calls_at_inference` == True / 0 in metrics (substrate-only gate logged)
  e. `cv` <= 0.10 for any config claiming PASS (cv > 0.10 = seed-unstable; demote)
  f. Anchor config (k=1 or ARM A equivalent) reproduces the expected baseline BPC within 0.05
     (verify by re-deriving from per_seed)
  g. Pre-reg direction check: if verdict claims HARD_PASS, the improvement direction must
     match {{PRE_REG_DIRECTION}} (large wrong-direction delta = HARD_FAIL per Skunkworks
     n3 SimVQ catch + Fix #5 sibling discipline)
  h. Corpus-provenance: `allow_synthetic=False` was honored (no "synthetic" flag in metrics)
  i. elapsed_s is non-trivially long (> 60s at full scale) — instant HARD_PASS is suspicious
  j. VERSION_MARKER: verify the run used the committed cell code, not a stale checkpoint
     from a different config (check CONFIG_VERSION in metrics matches the current cell code's
     CONFIG_VERSION constant)

  Re-derive cited numbers from per_seed (the dominant audit catch):
    python -c "
    import json, numpy as np
    m = json.load(open('data/exp_{{CELL_NAME}}/metrics.json'))
    pu = m.get('per_seed', [])
    bpcs = [e.get('substrate_bpc') for e in pu if e.get('substrate_bpc') is not None]
    mean_bpc = float(np.mean(bpcs)) if bpcs else None
    cv = float(np.std(bpcs) / max(np.mean(bpcs), 1e-9)) if bpcs else None
    print('n_per_unit:', len(pu))
    print('substrate_bpc mean (re-derived):', mean_bpc)
    print('cv (re-derived):', cv)
    print('verdict_msg (snippet):', m.get('verdict_msg','')[:300])
    print('zero_llm_calls_at_inference:', m.get('zero_llm_calls_at_inference'))
    "
    Confirm the re-derived mean matches the verdict_msg's cited number within 0.01.
    If it does NOT reproduce: flag as MISCITE. Do NOT forward a phantom number to Skunkworks.

### Disposition decision (your inline call — Skunkworks ratifies independently):

  Based on the pre-reg bands {{PRE_REG_BANDS}} and the re-derived numbers:

  - HARD_PASS candidate: cv <= 0.05 + direction correct + substrate-only gate + full-run
    + cited numbers reproduce from per_seed + anchor reproduces N2 baseline
  - MIDDLE_BAND: partial improvement, cv > 0.05 or direction correct but below HARD_PASS bar
  - HARD_FAIL: improvement below bar OR wrong direction OR substrate-only gate violated
  - HONEST_NEGATIVE: pre-reg miss; genuine on full data; not a calibration bug

  Commit full metrics:
    for i in 1 2 3; do [ ! -f .git/index.lock ] && break; sleep 2; done
    git add -- data/exp_{{CELL_NAME}}/metrics.json
    git add -- data/exp_{{CELL_NAME}}/partial_metrics_*.json  # if not gitignored
    git commit -m "exp: full metrics for {{CELL_NAME}} — <verdict>" \
      -- data/exp_{{CELL_NAME}}/metrics.json
    FULL_METRICS_COMMIT=$(git rev-parse --short HEAD)

---

## 8. A5-GATE ATOMIZE

**IMPORTANT:** You (the pipeline agent) do NOT write to the Store directly. Atomization
is cert-owner (Skunkworks) work. Your role here is to BUILD the cert_ledger_writer row
payload and pass it to Skunkworks via the completion note (Section 9), so they can do the
A5-gated write in their own window.

### Build the ledger row payload (do NOT call append_cert_ledger_row yourself):

  Determine disposition and build the appropriate row:

  For HARD_PASS (chain_grade, delta=+1):
    from tools.cert_ledger_writer import build_chain_grade_ruling_row
    row = build_chain_grade_ruling_row(
        atom_id='{{ATOM_ID_CANDIDATE}}',
        cell_commit='<FULL_METRICS_COMMIT_HASH>',
        verdict='HARD_PASS',
        notes_path='notes/{{CELL_NAME}}_pipeline_complete_<DATE>.md',
        metrics_path='data/exp_{{CELL_NAME}}/metrics.json',
        cv=<cv_value_from_per_seed>,
        cert_class='pre_reg_pass',
        atomized_by='skunkworks',
        note='pipeline_agent_{{CELL_NAME}}_chain_grade',
    )

  For MIDDLE_BAND / HARD_FAIL (measured_mechanism or honest_negative, delta=0):
    from tools.cert_ledger_writer import build_measured_mechanism_row, build_honest_negative_row
    # Use build_measured_mechanism_row for MM characterization
    # Use build_honest_negative_row for pre-reg miss (honest negative)
    row = build_measured_mechanism_row(
        atom_id='{{ATOM_ID_CANDIDATE}}',
        cell_commit='<FULL_METRICS_COMMIT_HASH>',
        verdict='MIDDLE_BAND',  # or 'HARD_FAIL'
        notes_path='notes/{{CELL_NAME}}_pipeline_complete_<DATE>.md',
        metrics_path='data/exp_{{CELL_NAME}}/metrics.json',
        atomized_by='skunkworks',
        note='pipeline_agent_{{CELL_NAME}}_measured_mechanism',
    )

  Print the row as JSON in the completion note for Skunkworks to copy-paste into their
  A5 window. Include the import statement they'll need.

  DO NOT call append_cert_ledger_row. DO NOT touch data/substrate_index. That is
  Skunkworks's exclusive single-writer window.

---

## 9. COMPLETION NOTE FORMAT

File a SINGLE note at:
  notes/{{CELL_NAME}}_pipeline_complete_<DATE>.md

(No "to_<role>" prefix in the filename — Fix #10: notes under Agent Teams are shared
artifacts, not addressed letters. The content includes routing asks by name.)

### Note template:

```
# Pipeline Complete: {{CELL_NAME}}

**Date:** <UTC date>
**Disposition:** <HARD_PASS / MIDDLE_BAND / HARD_FAIL / HONEST_NEGATIVE>
**Cell commit:** <commit hash>
**Full metrics commit:** <commit hash>
**Cert_ledger row hash:** (Skunkworks fills after A5 write)

## Key Numbers (re-derived from per_seed — not from verdict_msg)

- substrate_bpc mean: <X> (re-derived: <code snippet output>)
- cv: <X>
- zero_llm_calls_at_inference: <True/False>
- n_seeds completed: <N>
- Anchor reproduces baseline within 0.05: <YES/NO>
- Pre-reg direction honored: <YES/NO>

## Inline Disposition

<1-2 sentences explaining the disposition with the actual numbers.>
Pre-reg bands: {{PRE_REG_BANDS}}
Verdict: <your inline disposition + reason>
Note: Skunkworks will independently recompute off per_unit before ratifying cert-grade.

## Cert Ledger Row (for Skunkworks A5 window)

Skunkworks: copy this into your atomize tool's A5 window.

```python
from tools.cert_ledger_writer import build_<TYPE>_row, append_cert_ledger_row
row = <paste the built row dict here>
hash = append_cert_ledger_row(row,
    expected_cert_n_pre=<CURRENT_CERT_N>,
    expected_cert_n_post=<EXPECTED_CERT_N_POST>,
)
print("row_hash:", hash)
```

## Per-Unit Reconciliation

<table or list: per (seed, arm) substrate_bpc, cv, wall_s — re-derived from per_seed>

## Honest Scope

<1-2 sentences on what was tested, corpus, N_DIM, V_C, seeds. What this result DOES and
DOES NOT imply for the broader substrate capability.>

## Corpus-Provenance

- Corpus: {{CORPUS}}
- allow_synthetic=False: <confirmed / not confirmed>
- Data integrity check: <pass/fail>

## Artifacts

- Cell: {{CELL_FILE}} (commit <hash>)
- Pre-reg: {{PRE_REG_NOTES_PATH}} (commit <hash>)
- Smoke metrics: data/exp_{{CELL_NAME}}_smoke/metrics.json
- Full metrics: data/exp_{{CELL_NAME}}/metrics.json (commit <hash>)

## 2x-Revival Angle (required on HARD_FAIL / MIDDLE_BAND / HONEST_NEGATIVE)

<Mandatory if negative. Per USER standing: every cert-negative routes to Research for
a 2x/3x revival drill. Suggested angle based on the observed failure pattern.>

Research: please consider running a 2x-revival drill on this. Suggested angle: <angle>.

## Asks

- Skunkworks: please run independent landed-VET (re-derive from per_unit; verify corpus;
  check substrate-only gate; ratify or adjust inline disposition; do the A5-gated Store
  write if chain-grade; route negative to Research if not chain-grade)
- Research: <any specific asks — e.g., revival angle routing, director_plan.json update>
```

Commit the note:
  git add -- notes/{{CELL_NAME}}_pipeline_complete_<DATE>.md
  git commit -m "exp: pipeline completion note for {{CELL_NAME}} — <disposition>" \
    -- notes/{{CELL_NAME}}_pipeline_complete_<DATE>.md

---

## 10. REPLY-TO-PARENT FORMAT (Plain-English-First — Fix #13)

Reply to the Director (parent) with exactly this structure:

```
PIPELINE COMPLETE: {{CELL_NAME}}

Plain-English summary (2-3 sentences):
<What was tested, what happened, and what it means for the substrate in non-jargon terms.
e.g., "The kWTA soft-decode cell tested whether giving the substrate's decoder access to
multiple concept codes (instead of just one) improves language model BPC. The k=8 arm
lowered ceiling BPC from 2.05 to 1.72 bits — a meaningful improvement — but token-level
BPC dropped only 0.12 bits, below the HARD_PASS 0.21-bit bar. This is a partial mechanism
win: soft assignment helps the codebook floor but does not fully propagate to the token
prediction gap.">

Cert disposition: <HARD_PASS / MIDDLE_BAND / HARD_FAIL / HONEST_NEGATIVE>
Key numbers (re-derived): substrate_bpc=<X>, cv=<X>, zero_llm=<True/0>, n_seeds=<N>
Pre-reg direction honored: <YES/NO>
Inline verdict: <your call, e.g., "MIDDLE_BAND — mechanism confirmed, HARD_PASS bars missed">
Skunkworks ask: independent landed-VET pending (A5 row payload in completion note)

Artifacts:
  Completion note:  notes/{{CELL_NAME}}_pipeline_complete_<DATE>.md
  Full metrics:     data/exp_{{CELL_NAME}}/metrics.json (commit <hash>)
  Cell:             {{CELL_FILE}} (commit <hash>)

<If negative:>
2x-revival angle: <suggested angle> — routed to Research in completion note.
```

---

## FIX INVENTORY (baked into this template)

| Fix | Baked-in mechanism |
|---|---|
| Fix #1: at most 1 ScheduleWakeup | Explicit prohibition in prompt header; pipeline agent does NOT schedule wakeups |
| Fix #2: bundled spawn | This template IS the bundled spawn covering all 5+ sequential steps |
| Fix #3: per-seed runtime measured | Section 1e: near-full-scale single-seed timing required before full dispatch |
| Fix #4: no background bash watchers | Sections 3 + 6: in-spawn polling loops only |
| Fix #5: run_mode check first | Sections 4 + 7: run_mode check is the FIRST step in every VET |
| Fix #6: zero-D-overlap fallback | Section 1a: baked-in cell-authorship requirements; cited by name |
| Fix #7: status-line on long waits | Section 5c + 6: 30-min status-line cadence; Fix #7 status line before entering poll |
| Fix #8: parallel-work-backlog | This template is the parallel-work mechanism (Director main thread stays free) |
| Fix #9: codify-repeated-searches | Template itself captures reusable patterns for re-use |
| Fix #10: no to_role prefix | Section 9: completion note filename has no to_<role> prefix |
| Pre-reg-direction-must-honor-intent | Section 7g: explicit wrong-direction = HARD_FAIL check |
| Verify-off-DATA | Sections 4 + 7: re-derive cited numbers from per_seed before forwarding |
| A5 PRE/POST gating | Section 8: build row payload but defer A5-gated write to Skunkworks |
| Path-scoped commits | Sections 2a, 5a, 7, 9: all commits use explicit paths; no git add -A |
| .venv Python | Section 0b + throughout: .venv/Scripts/python.exe; NEVER system python |
| Substrate-only-decode gate | Sections 1a, 4d, 7d: zero_llm_calls_at_inference logged + checked |
| No ScheduleWakeup by cell-author | Explicit prohibition; only Director main thread may schedule |
| 2x-revival routing on negative | Section 9: mandatory 2x-revival angle in every negative completion note |

---

## SCHEDULEWAKEUP DISCIPLINE

The pipeline agent does NOT call ScheduleWakeup under any circumstances.
- Only the Director main thread schedules wakeups (Fix #1).
- At most one ScheduleWakeup per Director turn, at end of cycle.
- The pipeline agent signals completion by filing the completion note +
  replying to parent (Sections 9 + 10). The Director wakes when it polls
  notes/ or reads the reply.

---

## KNOWN GAPS / TODOs FOR FUTURE REFINEMENT

### TODO #1: GPU queue dispatch (overnight_queue)
- GPU cells require PROT-020 import-torch gate verification before dispatch.
- GPU cells may need explicit CUDA device index + HuggingFace offline mode flag.
- Runtime norms differ (ms/doc on GPU vs hundreds of ms on CPU; see Orchestrator
  handoff Section 7e runtime table).
- Push is harness-DENIED to exp_dev flavor; all GPU dispatches MUST route through
  Orchestrator. Template currently has a placeholder "route to Orchestrator" but
  the exact handoff protocol for the background-spawn case is not tested.
- The first GPU pipeline agent spawn should measure push-latency + Orchestrator
  response-time and add explicit timeout handling.

### TODO #2: Multi-arm cells with independent Store writes
- This template assumes one cell = one cert_ledger row.
- Multi-arm cells (e.g., 4-arm anisotropy rescue) may need per-arm disposition
  rows with independent atom IDs.
- The A5 single-writer constraint means all rows must be written in ONE Skunkworks
  window (not interleaved with another pipeline agent's write). Add explicit
  note to Skunkworks asking them to batch all arms in one A5 session.

### TODO #3: Long-wall full runs > 4h
- Template uses {{TIMEOUT_H}} = 4h default. Some full runs legitimately take longer
  (e.g., U1 FB15k-237 at 777s = ~13min, but multi-config GPU sweeps at scale).
- Add escalation logic: if ETA extrapolation from partials exceeds {{TIMEOUT_H}},
  surface to Director BEFORE timeout fires rather than letting the poll loop exhaust.

### TODO #4: Push-harness-DENIED branches
- Some agent flavors cannot push to origin/main (harness-DENIED).
- Template currently says "route to Orchestrator." The first use should verify:
  (a) which agent flavors can push, (b) what the exact Orchestrator hand-off message
  should look like, (c) how long the round-trip adds to the pipeline wall.

### TODO #5: Checkpoint-resume under STANDSTILL
- If USER issues a STANDSTILL mid-pipeline, the agent must stop.
- Current template has no STANDSTILL detection loop. Add: check for
  data/orchestrator_paused.flag at the start of each poll cycle; if present, stop +
  file a clean handoff note to Director.

### TODO #6: Smoke-to-full queue routing differences
- Smoke can go to local_cpu_queue (cheaper); full may need remote_cpu_queue or
  overnight_queue (GPU) depending on cell wall-time.
- Template currently uses the same {{QUEUE_TARGET}} for both. Consider splitting into
  {{SMOKE_QUEUE}} + {{FULL_QUEUE}} params on the next revision.

### TODO #7: per-seed checkpoint timing for the near-full-scale measurement (Fix #3)
- Current Section 1e uses smoke (--smoke flag) as a proxy for near-full-scale.
- For cells where smoke=tiny and full=giant (e.g., smoke N_DIM=512 vs full N_DIM=16384),
  smoke wall is not a reliable extrapolation base.
- Better: run a SINGLE SEED at full N_DIM but only 1 config arm (not the full k-grid).
  This requires a new CLI flag (--single-seed-timing) or a manual env override.
  First use of this template should validate the measurement approach.

---

## ESTIMATED TOKEN COST PER PIPELINE-AGENT SPAWN

Rough estimate for a typical N-series cell (pythia-160m residuals on remote_cpu_queue):

| Phase | Tokens (approx) |
|---|---|
| Startup / reading (Section 0) | ~5K |
| Cell authorship (Section 1, fork + bake-in) | ~15-25K |
| AST-check + self-test (Section 1b-d) | ~3K |
| Smoke dispatch + poll loop (Sections 2-3) | ~5K |
| Smoke-VET inline (Section 4) | ~8K |
| Full dispatch + poll loop (Sections 5-6) | ~10K |
| Full-VET inline (Section 7) | ~12K |
| Build cert row + write completion note (Sections 8-9) | ~8K |
| Reply to parent (Section 10) | ~2K |
| **Total (cell already authored, clean run)** | **~53-73K tokens** |
| **Total (cell needs authoring from scratch)** | **~70-100K tokens** |

Comparison: previous 5-spawn sequential pattern:
- cell-author spawn: ~40K
- smoke-VET spawn: ~30K
- full-dispatch spawn: ~20K
- full-VET spawn: ~40K
- atomize spawn: ~20K
- **Total (5 spawns):** ~150K tokens + main-thread coordination overhead

Estimated savings: 50-70% token reduction + eliminates main-thread tie-up for 4-6 hours.

---

*Template v1.0 — first 2-3 uses will discover edge cases (see TODOs above). After each
use, append a brief post-mortem section to this file documenting what worked, what failed,
and which TODO items need addressing. Treat the TODOs as the template's open-loop backlog.*
